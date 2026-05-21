import streamlit as st
import paho.mqtt.client as mqtt
import json
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="🐾 Coco & Canela",
    page_icon="🐾",
    layout="centered"
)

# ── CSS: fondo animado + todos los textos legibles ────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Pacifico&display=swap');

/* Fondo animado con gradiente que se mueve */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #f8b4c8, #ffd6a5, #fdffb6, #caffbf, #a0c4ff, #ffc6ff);
    background-size: 400% 400%;
    animation: gradientFlow 12s ease infinite;
    font-family: 'Nunito', sans-serif;
}

@keyframes gradientFlow {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Quitar fondo del header de Streamlit */
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }

/* Todos los textos en oscuro para legibilidad */
* { color: #2d2d2d !important; }

/* Tarjetas blancas con sombra suave */
.tarjeta {
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 22px 28px;
    margin: 12px 0;
    box-shadow: 0 6px 24px rgba(0,0,0,0.10);
    text-align: center;
    border: 1.5px solid rgba(255,255,255,0.9);
}

/* Título principal */
.titulo-principal {
    font-family: 'Pacifico', cursive;
    font-size: 2.6rem;
    text-align: center;
    color: #c0392b !important;
    text-shadow: 2px 3px 0px rgba(255,255,255,0.6);
    margin-bottom: 4px;
}

.subtitulo {
    text-align: center;
    font-size: 1.05rem;
    color: #555 !important;
    margin-bottom: 20px;
}

/* Pastillas de estado */
.pill {
    display: inline-block;
    padding: 8px 22px;
    border-radius: 30px;
    font-weight: 800;
    font-size: 1.1rem;
    margin-bottom: 6px;
    color: white !important;
}
.pill-coco    { background: linear-gradient(135deg, #27ae60, #2ecc71); }
.pill-canela  { background: linear-gradient(135deg, #e67e22, #f39c12); }
.pill-nadie   { background: linear-gradient(135deg, #95a5a6, #bdc3c7); }

.evento-texto {
    font-size: 0.85rem;
    color: #666 !important;
    margin-top: 4px;
}

/* Botones de Streamlit más bonitos */
[data-testid="stButton"] > button {
    border-radius: 14px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 10px 8px !important;
    border: none !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    color: white !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 18px rgba(0,0,0,0.18) !important;
}

/* Colores individuales por posición */
[data-testid="column"]:nth-child(1) button { background: linear-gradient(135deg,#27ae60,#2ecc71) !important; }
[data-testid="column"]:nth-child(2) button { background: linear-gradient(135deg,#e67e22,#f39c12) !important; }
[data-testid="column"]:nth-child(3) button { background: linear-gradient(135deg,#95a5a6,#636e72) !important; }

/* Secciones con título */
.seccion-titulo {
    font-size: 1.2rem;
    font-weight: 800;
    color: #2d2d2d !important;
    margin: 18px 0 6px 0;
}

/* Alerts de Streamlit: forzar texto oscuro */
[data-testid="stAlert"] p,
[data-tes
