import streamlit as st
import requests

st.set_page_config(page_title="Dollar Tracker Argentina", layout="centered")

st.title("💵 Real-time Dollar Monitor - Argentina")
st.markdown("Track official, blue, MEP and other dollar exchange rates in real time.")

st.sidebar.header("🔔 Alert Settings")
alert_config = {}
dollar_types = ['oficial', 'blue', 'mep', 'ccL', 'turista', 'cripto']

for d_type in dollar_types:
    with st.sidebar.expander(f"{d_type.capitalize()} dollar"):
        up = st.number_input(f"Alert ↑ % if {d_type} increases", min_value=0.0, value=1.0, step=0.5, key=f"{d_type}_up")
        down = st.number_input(f"Alert ↓ % if {d_type} decreases", min_value=0.0, value=1.0, step=0.5, key=f"{d_type}_down")
        alert_config[d_type] = {'up': up, 'down': down}

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("🔁 Auto-refresh every 30s", value=False)

@st.cache_data(ttl=30)
def get_dollar_prices():
    try:
        url = "https://api.bluelytics.com.ar/v2/latest"
        response = requests.get(url)
        data = response.json()
        return {
            'oficial': data['oficial']['value_avg'],
            'blue': data['blue']['value_avg'],
            'mep': data.get('oficial_euro', {}).get('value_avg', 0),
            'ccL': data.get('blue_euro', {}).get('value_avg', 0),
            'turista': data['oficial']['value_sell'] * 1.3,
            'cripto': data['blue']['value_sell'] * 1.1,
        }
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return {}

if 'last_values' not in st.session_state:
    st.session_state.last_values = {}

current_values = get_dollar_prices()
for d_type, current_value in current_values.items():
    last_value = st.session_state.last_values.get(d_type, current_value)
    change = ((current_value - last_value) / last_value) * 100 if last_value else 0

    col1, col2 = st.columns([2, 1])
    col1.metric(f"{d_type.capitalize()} dollar", f"${current_value:.2f}", f"{change:+.2f}%")

    if change >= alert_config[d_type]['up']:
        st.warning(f"⚠️ {d_type.capitalize()} dollar increased by {change:.2f}%")
    elif change <= -alert_config[d_type]['down']:
        st.error(f"🔻 {d_type.capitalize()} dollar decreased by {change:.2f}%")

    st.session_state.last_values[d_type] = current_value

if auto_refresh:
    st.experimental_rerun()
