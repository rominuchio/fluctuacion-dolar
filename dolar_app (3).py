
import streamlit as st
import requests
from datetime import datetime

st.set_page_config("Dólar Argentina", layout="wide")

st.title("💱 Monitor de Dólares – Argentina")
st.caption(f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Selección de tipos
types = {
    "oficial": "Dólar Oficial",
    "blue": "Dólar Blue",
    "bolsa": "Dólar Bolsa",
    "contadoconliqui": "CCL",
    "turista": "Dólar Turista",
    "cripto": "Dólar Cripto"
}

# Alertas
st.sidebar.header("🔔 Alertas")
alert = {
    t: {
        "up": st.sidebar.number_input(f"↑ % {types[t]}", key=f"{t}_up", value=1.0, step=0.5),
        "down": st.sidebar.number_input(f"↓ % {types[t]}", key=f"{t}_down", value=1.0, step=0.5)
    } for t in types
}

if st.sidebar.button("🔄 Actualizar"):
    st.experimental_rerun()

@st.cache_data(ttl=60)
def fetch_data():
    url = "https://dolarapi.com/v1/cotizaciones"
    resp = requests.get(url)
    return {d["moneda"]: d for d in resp.json()}

data = fetch_data()
cols = st.columns(len(types))

for idx, (k, name) in enumerate(types.items()):
    d = data.get(k)
    if not d:
        cols[idx].write(f"{name} no disponible")
        continue

    compra = float(d["compra"])
    venta = float(d["venta"])
    prev = st.session_state.get(f"prev_{k}", compra)
    variation = (compra - prev)/prev*100 if prev != 0 else 0

    cols[idx].metric(f"{name}", f"Compra: ${compra:.2f}", f"{variation:+.2f}%")
    cols[idx].write(f"Venta: **${venta:.2f}**")

    if variation >= alert[k]["up"]:
        cols[idx].warning(f"{name} subió {variation:.2f}% 📈")
    elif variation <= -alert[k]["down"]:
        cols[idx].error(f"{name} bajó {variation:.2f}% 📉")

    st.session_state[f"prev_{k}"] = compra
