import streamlit as st
import os
import requests
from docx import Document
from io import BytesIO
import PyPDF2

# 1. CONFIGURACIÓN DE USUARIOS
USUARIOS_PERMITIDOS = {
    "admin": "clave777",
    "user1": "peru2026",
    "user2": "legal20",
    "user3": "pjia01",
    "user4": "estudio5"
}

def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if not st.session_state.autenticado:
        st.set_page_config(page_title="Login P&JIA", page_icon="🔐")
        st.title("🔐 Acceso Privado P&JIA")
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user in USUARIOS_PERMITIDOS and USUARIOS_PERMITIDOS[user] == password:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        return False
    return True

if not login():
    st.stop()

# --- CONFIGURACIÓN DE IA ---
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("🚨 ERROR: No se encontró la clave 'GROQ_API_KEY' en los Secrets de Streamlit.")
    st.stop()

st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")

with st.sidebar:
    st.title("🛠️ Panel de Control")
    opcion = st.selectbox("Selecciona:", ["Asistente Legal", "Calculadora Laboral", "Generador de Documentos"])
    archivo_subido = st.file_uploader("📁 Analizar PDF", type=['pdf'])
    if st.button("🗑️ Limpiar Historial"):
        st.session_state.messages = []
        st.rerun()

def extraer_pdf(archivo):
    lector = PyPDF2.PdfReader(archivo)
    return "".join([p.extract_text() for p in lector.pages])

if "messages" not in st.session_state:
    st.session_state.messages = []

if opcion == "Asistente Legal":
    st.title("⚖️ Asistente Jurídico Inteligente")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Consulta la ley..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                ctx = f"\nDoc: {extraer_pdf(archivo_subido)}" if archivo_subido else ""
                res = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json={
                        "model": "llama3-70b-8192",
                        "messages": [
                            {"role": "system", "content": "Eres P&JIA Core. Experto legal peruano. Cita leyes reales (DL 728, Código Civil/Penal). No inventes nada."},
                            {"role": "user", "content": prompt + ctx}
                        ],
                        "temperature": 0.1
                    }
                )
                data = res.json()
                # --- AQUÍ ESTÁ EL ARREGLO PARA EL ERROR ---
                if "choices" in data:
                    texto = data["choices"][0]["message"]["content"]
                    st.markdown(texto)
                    st.session_state.messages.append({"role": "assistant", "content": texto})
                else:
                    msg_error = data.get("error", {}).get("message", "Error desconocido")
                    st.error(f"La IA respondió un error: {msg_error}")
            except Exception as e:
                st.error(f"Fallo de conexión: {e}")

# (Mantener las otras opciones igual o simplificadas para evitar errores)
