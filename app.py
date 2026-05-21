import streamlit as st
import paho.mqtt.client as mqtt
import json
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="🐾 Mis Mascotas",
    page_icon="🐾",
    layout="centered"
)

# ── Estilos visuales ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #fff8f0; }
    .titulo { text-align: center; font-size: 2.5rem; color: #c0392b; }
    .subtitulo { text-align: center; color: #888; font-size: 1rem; }
    .tarjeta {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
    }
    .estado-pill {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Encabezado ────────────────────────────────────────────────────────────────
st.markdown('<p class="titulo">🐾 Comedero de Coco y Canela</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Controla la alimentación de tus mininos desde donde estés 🏠</p>', unsafe_allow_html=True)
st.markdown("---")

# ── MQTT ─────────────────────────────────────────────────────────────────────
BROKER_IP   = "157.230.214.127"
PORT        = 1883
TOPIC       = "cmqtt_sdesi"
CLIENT_ID   = "app_usuario_mascotas_01"

@st.cache_resource
def conectar_mqtt():
    cliente = mqtt.Client(CLIENT_ID)
    try:
        cliente.connect(BROKER_IP, PORT, 60)
        cliente.loop_start()
    except Exception as e:
        st.error(f"⚠️ No se pudo conectar al broker MQTT: {e}")
    return cliente

client = conectar_mqtt()

def enviar_comando(pantalla: str, motor: str):
    payload = json.dumps({"Pantalla": pantalla, "Act1": motor})
    try:
        client.publish(TOPIC, payload, qos=1)
        return True
    except Exception as e:
        st.error(f"Error enviando comando: {e}")
        return False

# ── Estado de sesión ──────────────────────────────────────────────────────────
if "motor_actual" not in st.session_state:
    st.session_state.motor_actual = "NADIE"
if "ultimo_evento" not in st.session_state:
    st.session_state.ultimo_evento = "Sin actividad reciente"

# ── Cámara en vivo ────────────────────────────────────────────────────────────
st.markdown("### 📷 Cámara en vivo")
st.markdown(
    '<div class="tarjeta">Activa la cámara para ver a tus mininos 🐱</div>',
    unsafe_allow_html=True
)
camara = st.camera_input("Ver a mis mascotas")
if camara:
    st.image(camara, caption="📸 Vista en vivo", use_container_width=True)

st.markdown("---")

# ── Estado actual ─────────────────────────────────────────────────────────────
st.markdown("### 🔔 Estado del comedero")
color_map = {"GATO_A": "#27ae60", "GATO_B": "#e67e22", "NADIE": "#95a5a6"}
label_map = {"GATO_A": "🟢 Plato de Coco abierto",
             "GATO_B": "🟠 Plato de Canela abierto",
             "NADIE":  "⚪ Comederos cerrados"}
color  = color_map[st.session_state.motor_actual]
etiq   = label_map[st.session_state.motor_actual]

st.markdown(
    f'<div class="tarjeta">'
    f'<span class="estado-pill" style="background:{color};color:white">{etiq}</span>'
    f'<br><small style="color:#aaa">Último evento: {st.session_state.ultimo_evento}</small>'
    f'</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# ── Botones manuales ──────────────────────────────────────────────────────────
st.markdown("### 🍽️ Control manual")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🐱 Abrir Coco", use_container_width=True):
        if enviar_comando("Coco", "GATO_A"):
            st.session_state.motor_actual = "GATO_A"
            st.session_state.ultimo_evento = "Botón: plato de Coco"
            st.success("¡Plato de Coco abierto! 🟢")
            st.rerun()

with col2:
    if st.button("🐱 Abrir Canela", use_container_width=True):
        if enviar_comando("Canela", "GATO_B"):
            st.session_state.motor_actual = "GATO_B"
            st.session_state.ultimo_evento = "Botón: plato de Canela"
            st.success("¡Plato de Canela abierto! 🟠")
            st.rerun()

with col3:
    if st.button("🔒 Cerrar todo", use_container_width=True):
        if enviar_comando("Nadie", "NADIE"):
            st.session_state.motor_actual = "NADIE"
            st.session_state.ultimo_evento = "Botón: cerrar comederos"
            st.warning("Comederos cerrados ⚪")
            st.rerun()

st.markdown("---")

# ── Control por voz ───────────────────────────────────────────────────────────
st.markdown("### 🎙️ Hablarle a mis mininos / Comando de voz")
st.write("Di: *'abrir coco'*, *'abrir canela'* o *'cerrar'*")

audio = mic_recorder(
    start_prompt="🎤 Hablar",
    stop_prompt="🟥 Detener",
    just_once=True,
    format="wav",
    key="voz_usuario"
)

if audio:
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio["bytes"])) as source:
            audio_data = recognizer.record(source)
            texto = recognizer.recognize_google(audio_data, language="es-ES")
            st.info(f"🗣️ Escuché: *\"{texto}\"*")
            cmd = texto.lower()

            if "coco" in cmd:
                enviar_comando("Coco", "GATO_A")
                st.session_state.motor_actual = "GATO_A"
                st.session_state.ultimo_evento = "Voz: Coco"
                st.success("¡Voz aceptada! Abriendo plato de Coco 🐱")
                st.rerun()

            elif "canela" in cmd:
                enviar_comando("Canela", "GATO_B")
                st.session_state.motor_actual = "GATO_B"
                st.session_state.ultimo_evento = "Voz: Canela"
                st.success("¡Voz aceptada! Abriendo plato de Canela 🐱")
                st.rerun()

            elif any(p in cmd for p in ["cerrar", "cierra", "nadie", "quitar"]):
                enviar_comando("Nadie", "NADIE")
                st.session_state.motor_actual = "NADIE"
                st.session_state.ultimo_evento = "Voz: cerrar"
                st.warning("Comederos cerrados por voz ⚪")
                st.rerun()

            else:
                st.warning("No reconocí ese comando. Intenta con 'Coco', 'Canela' o 'Cerrar'.")

    except sr.UnknownValueError:
        st.error("No pude entender el audio. ¿Puedes repetirlo?")
    except sr.RequestError as e:
        st.error(f"Error con el servicio de voz: {e}")

# ── Pie de página ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#ccc;font-size:0.8rem">🐾 Hecho con amor para Coco y Canela</p>',
    unsafe_allow_html=True
)
