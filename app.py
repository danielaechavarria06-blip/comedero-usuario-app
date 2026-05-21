import streamlit as st
import paho.mqtt.client as mqtt
import json
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io

st.set_page_config(
    page_title="Coco & Canela",
    page_icon="🐾",
    layout="centered"
)

# Estrellitas animadas con canvas + fondo degradado
st.components.v1.html(
    '''
    <style>
      #starCanvas {
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        z-index: 0;
        pointer-events: none;
      }
    </style>
    <canvas id="starCanvas"></canvas>
    <script>
      const canvas = document.getElementById("starCanvas");
      const ctx = canvas.getContext("2d");
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;

      const stars = Array.from({length: 80}, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 3 + 1,
        dx: (Math.random() - 0.5) * 0.6,
        dy: (Math.random() - 0.5) * 0.6,
        alpha: Math.random(),
        dAlpha: (Math.random() - 0.5) * 0.02,
        color: ["#ffb3c6","#ffd6a5","#caffbf","#a0c4ff","#ffc6ff","#fdffb6"][Math.floor(Math.random()*6)]
      }));

      function drawStar(x, y, r, alpha, color) {
        ctx.save();
        ctx.globalAlpha = Math.max(0.2, Math.min(1, alpha));
        ctx.fillStyle = color;
        ctx.shadowColor = color;
        ctx.shadowBlur = 8;
        ctx.beginPath();
        for (let i = 0; i < 5; i++) {
          const angle = (i * 4 * Math.PI) / 5 - Math.PI / 2;
          const outerX = x + r * Math.cos(angle);
          const outerY = y + r * Math.sin(angle);
          const innerAngle = angle + (2 * Math.PI) / 10;
          const innerX = x + (r * 0.4) * Math.cos(innerAngle);
          const innerY = y + (r * 0.4) * Math.sin(innerAngle);
          if (i === 0) ctx.moveTo(outerX, outerY);
          else ctx.lineTo(outerX, outerY);
          ctx.lineTo(innerX, innerY);
        }
        ctx.closePath();
        ctx.fill();
        ctx.restore();
      }

      function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        stars.forEach(s => {
          s.x += s.dx;
          s.y += s.dy;
          s.alpha += s.dAlpha;
          if (s.alpha <= 0.1 || s.alpha >= 1) s.dAlpha *= -1;
          if (s.x < 0) s.x = canvas.width;
          if (s.x > canvas.width) s.x = 0;
          if (s.y < 0) s.y = canvas.height;
          if (s.y > canvas.height) s.y = 0;
          drawStar(s.x, s.y, s.r * 4, s.alpha, s.color);
        });
        requestAnimationFrame(animate);
      }
      animate();

      window.addEventListener("resize", () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      });
    </script>
    ''',
    height=0
)

st.markdown(
    '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Pacifico&display=swap');

[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #f8b4c8, #ffd6a5, #fdffb6, #caffbf, #a0c4ff, #ffc6ff);
    background-size: 400% 400%;
    animation: gradientFlow 12s ease infinite;
    font-family: "Nunito", sans-serif;
}

@keyframes gradientFlow {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }

* { color: #2d2d2d !important; }

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

.titulo-principal {
    font-family: "Pacifico", cursive;
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

.pill {
    display: inline-block;
    padding: 8px 22px;
    border-radius: 30px;
    font-weight: 800;
    font-size: 1.1rem;
    margin-bottom: 6px;
    color: white !important;
    -webkit-text-fill-color: white !important;
}
.pill-coco   { background: linear-gradient(135deg, #27ae60, #2ecc71); }
.pill-canela { background: linear-gradient(135deg, #e67e22, #f39c12); }
.pill-nadie  { background: linear-gradient(135deg, #95a5a6, #bdc3c7); }

.evento-texto {
    font-size: 0.85rem;
    color: #666 !important;
    margin-top: 4px;
}

.seccion-titulo {
    font-size: 1.2rem;
    font-weight: 800;
    color: #2d2d2d !important;
    margin: 18px 0 6px 0;
}

[data-testid="stButton"] > button {
    border-radius: 14px !important;
    font-family: "Nunito", sans-serif !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    padding: 12px 8px !important;
    border: none !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 18px rgba(0,0,0,0.25) !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
}
[data-testid="stButton"] > button p,
[data-testid="stButton"] > button span,
[data-testid="stButton"] > button div {
    color: white !important;
    -webkit-text-fill-color: white !important;
}

[data-testid="column"]:nth-child(1) button {
    background: linear-gradient(135deg, #27ae60, #2ecc71) !important;
    box-shadow: 0 4px 14px rgba(39,174,96,0.4) !important;
}
[data-testid="column"]:nth-child(2) button {
    background: linear-gradient(135deg, #e67e22, #f39c12) !important;
    box-shadow: 0 4px 14px rgba(230,126,34,0.4) !important;
}
[data-testid="column"]:nth-child(3) button {
    background: linear-gradient(135deg, #e74c3c, #c0392b) !important;
    box-shadow: 0 4px 14px rgba(231,76,60,0.4) !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stAlert"] span {
    color: #2d2d2d !important;
    -webkit-text-fill-color: #2d2d2d !important;
}

[data-testid="stCameraInput"] label {
    color: #2d2d2d !important;
    font-weight: 600;
}

.tarjeta-voz {
    background: linear-gradient(135deg, rgba(160,196,255,0.5), rgba(255,198,255,0.5));
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 22px 28px;
    margin: 12px 0;
    box-shadow: 0 6px 24px rgba(0,0,0,0.10);
    text-align: center;
    border: 1.5px solid rgba(255,255,255,0.9);
    font-size: 1.05rem;
    font-weight: 700;
}

hr { border: none; border-top: 2px dashed rgba(0,0,0,0.12) !important; margin: 18px 0; }

.footer {
    text-align: center;
    font-size: 0.85rem;
    color: #888 !important;
    margin-top: 30px;
    padding-bottom: 20px;
}
</style>
    ''',
    unsafe_allow_html=True
)

# Banner portada
st.image("banner.png", use_container_width=True)

# Encabezado
st.markdown('<p class="titulo-principal">🐾 Coco & Canela</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Cuida a tus mininos desde donde estes 🏠✨</p>', unsafe_allow_html=True)
st.markdown("---")

# MQTT
BROKER_IP = "157.230.214.127"
PORT      = 1883
TOPIC     = "cmqtt_sdesi"
CLIENT_ID = "app_usuario_mascotas_01"

@st.cache_resource
def conectar_mqtt():
    try:
        cliente = mqtt.Client(CLIENT_ID)
        cliente.connect(BROKER_IP, PORT, 60)
        cliente.loop_start()
        return cliente
    except Exception as e:
        st.error(f"No se pudo conectar al broker MQTT: {e}")
        return None

client = conectar_mqtt()

def enviar_comando(pantalla, motor):
    if client is None:
        st.error("Sin conexion MQTT.")
        return False
    payload = json.dumps({"Pantalla": pantalla, "Act1": motor})
    try:
        client.publish(TOPIC, payload, qos=1)
        return True
    except Exception as e:
        st.error(f"Error enviando comando: {e}")
        return False

# Estado de sesion
if "motor_actual" not in st.session_state:
    st.session_state.motor_actual = "NADIE"
if "ultimo_evento" not in st.session_state:
    st.session_state.ultimo_evento = "Sin actividad reciente"

# Camara en vivo
st.markdown('<p class="seccion-titulo">📷 Camara en vivo</p>', unsafe_allow_html=True)
st.markdown('<div class="tarjeta">👀 Activa la camara para ver a tus mininos en tiempo real 🐱</div>', unsafe_allow_html=True)
camara = st.camera_input("Captura una foto de tus gatitos")
if camara:
    st.image(camara, caption="Vista en vivo", use_container_width=True)

st.markdown("---")

# Estado actual
st.markdown('<p class="seccion-titulo">🔔 Estado del comedero</p>', unsafe_allow_html=True)

pill_class = {"GATO_A": "pill-coco", "GATO_B": "pill-canela", "NADIE": "pill-nadie"}
label_map  = {
    "GATO_A": "🟢 Plato de Coco abierto",
    "GATO_B": "🟠 Plato de Canela abierto",
    "NADIE":  "⚪ Comederos cerrados"
}

st.markdown(
    '<div class="tarjeta">'
    '<span class="pill ' + pill_class[st.session_state.motor_actual] + '">'
    + label_map[st.session_state.motor_actual] +
    '</span>'
    '<p class="evento-texto">Ultimo evento: ' + st.session_state.ultimo_evento + '</p>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# Botones manuales
st.markdown('<p class="seccion-titulo">🍽️ Control manual</p>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🐱 Abrir Coco", use_container_width=True):
        if enviar_comando("Coco", "GATO_A"):
            st.session_state.motor_actual = "GATO_A"
            st.session_state.ultimo_evento = "Boton: plato de Coco"
            st.rerun()

with col2:
    if st.button("🐱 Abrir Canela", use_container_width=True):
        if enviar_comando("Canela", "GATO_B"):
            st.session_state.motor_actual = "GATO_B"
            st.session_state.ultimo_evento = "Boton: plato de Canela"
            st.rerun()

with col3:
    if st.button("🔒 Cerrar todo", use_container_width=True):
        if enviar_comando("Nadie", "NADIE"):
            st.session_state.motor_actual = "NADIE"
            st.session_state.ultimo_evento = "Boton: cerrar comederos"
            st.rerun()

st.markdown("---")

# Control por voz
st.markdown('<p class="seccion-titulo">🎙️ Comando de voz</p>', unsafe_allow_html=True)
st.markdown(
    '<div class="tarjeta-voz">'
    '🗣️ Di: <b>abrir coco</b>, <b>abrir canela</b> o <b>cerrar</b><br>'
    '<span style="font-size:0.85rem;color:#888 !important;">Presiona el boton y habla claramente</span>'
    '</div>',
    unsafe_allow_html=True
)

audio = mic_recorder(
    start_prompt="🎤✨ Presiona para hablar con tus mininos",
    stop_prompt="🟥 Detener grabacion",
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
            st.info(f"🗣️ Escuche: {texto}")
            cmd = texto.lower()

            if "coco" in cmd:
                enviar_comando("Coco", "GATO_A")
                st.session_state.motor_actual = "GATO_A"
                st.session_state.ultimo_evento = "Voz: Coco"
                st.success("Abriendo plato de Coco 🐱")
                st.rerun()
            elif "canela" in cmd:
                enviar_comando("Canela", "GATO_B")
                st.session_state.motor_actual = "GATO_B"
                st.session_state.ultimo_evento = "Voz: Canela"
                st.success("Abriendo plato de Canela 🐱")
                st.rerun()
            elif any(p in cmd for p in ["cerrar", "cierra", "nadie", "quitar"]):
                enviar_comando("Nadie", "NADIE")
                st.session_state.motor_actual = "NADIE"
                st.session_state.ultimo_evento = "Voz: cerrar"
                st.warning("Comederos cerrados 🔒")
                st.rerun()
            else:
                st.warning("No reconoci ese comando. Intenta con Coco, Canela o Cerrar.")

    except sr.UnknownValueError:
        st.error("No pude entender el audio. Puedes repetirlo?")
    except sr.RequestError as e:
        st.error(f"Error con el servicio de voz: {e}")

# Footer
st.markdown('<p class="footer">🐾 Hecho con amor para Coco y Canela 💕</p>', unsafe_allow_html=True)
