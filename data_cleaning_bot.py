import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import norm
import datetime

# -----------------------------
# 🌗 Theme Toggle (Light/Dark)
# -----------------------------
theme = st.radio("Choose Theme:", ["Dark", "Light"], horizontal=True)

if theme == "Dark":
    bg_color = "#1c1c1e"
    text_color = "#ffffff"
    container_bg = "rgba(255, 255, 255, 0.1)"
else:
    bg_color = "#F0FFFF"  # Aqua white
    text_color = "#000000"
    container_bg = "rgba(255, 255, 255, 0.85)"


# -----------------------------
# 🎨 Custom Styling & Fonts
# -----------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
        background-color: {bg_color};
        color: {text_color};
    }}

    .stApp {{
        background-color: {bg_color};
    }}

    .glass {{
        background: {container_bg};
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }}

    .title-text {{
        text-align: center;
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 10px;
    }}

    .section-title {{
        text-align: center;
        font-size: 20px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }}

    hr {{
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 20px 0;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 📊 App Title
# -----------------------------
st.markdown("<div class='title-text'>📈 Options Strategy Predictor</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# -----------------------------
# 📥 Input Form
# -----------------------------
with st.form("input_form"):
    st.markdown("<div class='section-title'>💡 Input Parameters</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='glass'>", unsafe_allow_html=True)

        ticker = st.text_input("Stock Ticker", "AAPL").upper()
        num_contracts = st.number_input("Number of Contracts", min_value=1, value=1)
        percent_up = st.number_input("Stock Move Up (%)", min_value=1, max_value=500, value=10)
        percent_down = st.number_input("Stock Move Down (%)", min_value=1, max_value=500, value=10)

        exp_date = None
        chosen_strike = None

        if ticker:
            stock = yf.Ticker(ticker)
            expirations = stock.options
            exp_date = st.selectbox("Select Expiration Date", expirations)

            options_chain = stock.option_chain(exp_date)
            calls = options_chain.calls[['strike', 'lastPrice']]
            puts = options_chain.puts[['strike', 'lastPrice']]
            available_strikes = sorted(list(set(calls['strike']).intersection(set(puts['strike']))))
            chosen_strike = st.selectbox("Select Strike Price", available_strikes)

        st.markdown("</div>", unsafe_allow_html=True)

    submit_button = st.form_submit_button("🎯 Run Strategy Analysis")

# -----------------------------
# 🚀 After Submit
# -----------------------------
if submit_button and ticker and exp_date and chosen_strike:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📊 Market Overview</div>", unsafe_allow_html=True)

    history = stock.history(period="250d")
    current_price = history['Close'].iloc[-1]
    st.markdown(f"<p style='text-align: center;'>Current Stock Price: <strong>${current_price:.2f}</strong></p>", unsafe_allow_html=True)

    # Moving Averages
    ma_5 = history['Close'].rolling(window=5).mean().iloc[-1]
    ma_10 = history['Close'].rolling(window=10).mean().iloc[-1]
    ma_50 = history['Close'].rolling(window=50).mean().iloc[-1]
    ma_200 = history['Close'].rolling(window=200).mean().iloc[-1]

    st.markdown(f"""
        <div class='glass'>
        <p style='text-align: center;'>📉 5D: <strong>${ma_5:.2f}</strong> | 10D: <strong>${ma_10:.2f}</strong><br>
        📊 50D: <strong>${ma_50:.2f}</strong> | 200D: <strong>${ma_200:.2f}</strong></p>
        </div>
    """, unsafe_allow_html=True)

    # Trend Detection
    if current_price > ma_5 and current_price > ma_10 and current_price > ma_50 and current_price > ma_200:
        trend = "Uptrend 📈"
    elif current_price < ma_5 and current_price < ma_10 and current_price < ma_50 and current_price < ma_200:
        trend = "Downtrend 📉"
    else:
        trend = "Sideways ➖"

    st.markdown(f"<div class='section-title'>📍 Detected Trend: <strong>{trend}</strong></div>", unsafe_allow_html=True)

    # Volatility + Probabilities
    history['Return'] = history['Close'].pct_change()
    volatility = history['Return'].std()
    expiry_date = datetime.datetime.strptime(exp_date, "%Y-%m-%d")
    days_to_expiry = (expiry_date - datetime.datetime.today()).days

    if volatility == 0 or days_to_expiry <= 0:
        st.error("⚠️ Not enough volatility data or invalid expiration.")
    else:
        annual_vol = volatility * np.sqrt(252)
        daily_vol = annual_vol / np.sqrt(252)

        z_up = (percent_up / 100) / (daily_vol * np.sqrt(days_to_expiry))
        z_down = (-percent_down / 100) / (daily_vol * np.sqrt(days_to_expiry))

        prob_up = 1 - norm.cdf(z_up)
        prob_down = norm.cdf(z_down)
        prob_flat = 1 - (prob_up + prob_down)

        # Adjust based on trend
        if "Uptrend" in trend:
            prob_up *= 1.10
            prob_down *= 0.90
        elif "Downtrend" in trend:
            prob_down *= 1.10
            prob_up *= 0.90
        else:
            prob_flat *= 1.10

        # Normalize
        total = prob_up + prob_down + prob_flat
        prob_up /= total
        prob_down /= total
        prob_flat /= total

        st.markdown(f"""
            <div class='glass'>
            <div class='section-title'>📐 Adjusted Scenario Probabilities</div>
            <ul>
            <li><strong>Stock Up > +{percent_up}%</strong>: <span style='color: green;'>{prob_up:.2%}</span></li>
            <li><strong>Stock Down > -{percent_down}%</strong>: <span style='color: red;'>{prob_down:.2%}</span></li>
            <li><strong>Flat/Neutral</strong>: <span style='color: orange;'>{prob_flat:.2%}</span></li>
            </ul>
            </div>
        """, unsafe_allow_html=True)

        # Payoff Matrix
        shares = 100
        strategies = ['Buy Call', 'Buy Put', 'Write Call', 'Write Put']
        scenarios = [f'Stock Up {percent_up}%', f'Stock Down {percent_down}%', 'Flat']
        matrix = []

        for strat in strategies:
            row = []
            for scenario in scenarios:
                if scenario.startswith("Stock Up"):
                    new_price = chosen_strike * (1 + percent_up / 100)
                elif scenario.startswith("Stock Down"):
                    new_price = chosen_strike * (1 - percent_down / 100)
                else:
                    new_price = chosen_strike

                call_price = calls.loc[calls['strike'] == chosen_strike, 'lastPrice'].values[0]
                put_price = puts.loc[puts['strike'] == chosen_strike, 'lastPrice'].values[0]

                if strat == "Buy Call":
                    payoff = (max(0, new_price - chosen_strike) - call_price) * shares * num_contracts
                elif strat == "Buy Put":
                    payoff = (max(0, chosen_strike - new_price) - put_price) * shares * num_contracts
                elif strat == "Write Call":
                    payoff = (call_price - max(0, new_price - chosen_strike)) * shares * num_contracts
                elif strat == "Write Put":
                    payoff = (put_price - max(0, chosen_strike - new_price)) * shares * num_contracts
                row.append(round(payoff, 2))
            matrix.append(row)

        df = pd.DataFrame(matrix, index=strategies, columns=scenarios)
        st.dataframe(df.style.set_table_attributes("style='margin-left: auto; margin-right: auto;'"))

        # Strategy Picks
        st.markdown("<div class='section-title'>🎯 Strategy Recommendations</div>", unsafe_allow_html=True)
        probs = [prob_up, prob_down, prob_flat]
        row_mins = np.min(matrix, axis=1)
        minimax_value = np.max(row_mins)
        minimax_strategy = strategies[np.argmax(row_mins)]
        expected_values = np.dot(matrix, probs)
        best_ev_strategy = strategies[np.argmax(expected_values)]

        st.markdown(f"<p style='text-align: center;'>🛡 <strong>Minimax:</strong> {minimax_strategy} (${minimax_value:.2f} worst-case)</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>📊 <strong>Expected Value:</strong> {best_ev_strategy} (${expected_values[np.argmax(expected_values)]:.2f} avg)</p>", unsafe_allow_html=True)
