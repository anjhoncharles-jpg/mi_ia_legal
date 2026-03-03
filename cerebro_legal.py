import streamlit as st
import os

# Configuración de los 5 usuarios (No cambies las palabras en inglés)
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

# --- AQUÍ EMPIEZA TU CÓDIGO ORIGINAL ---
st.title("⚖️ P&JIA Core")
# Pega debajo de esto el resto de tu código que ya funcionaba
