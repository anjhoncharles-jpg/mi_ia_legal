import streamlit as st
import os

# 1. Configuración de Usuarios (Asegúrate de escribirlos igual al loguearte)
USUARIOS_PERMITIDOS = {
    "admin": "clave777",
    "user1": "peru2026"
}

# 2. Función de Login
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

# 3. Control de acceso
if not login():
    st.stop()

# --- AQUÍ EMPIEZA TU CÓDIGO DE P&JIA Core ---
st.title("⚖️ P&JIA Core")
# Agrega aquí el resto de tu código original...
