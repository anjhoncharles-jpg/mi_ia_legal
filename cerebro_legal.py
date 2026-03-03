import streamlit as st
import requests
from docx import Document
from io import BytesIO
import streamlit as st

# Configuración de los 5 usuarios autorizados
USUARIOS_PERMITIDOS = {
    "admin": "clave777",
    "user1": "peru2026",
    "user2": "legal01",
    "user3": "mineria5",
    "user4": "estudio20"
}

def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
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

# Si no está logueado, detiene el resto del código
if not login():
    st.stop()

# --- AQUÍ EMPIEZA TU CÓDIGO ACTUAL (P&JIA Core) ---
