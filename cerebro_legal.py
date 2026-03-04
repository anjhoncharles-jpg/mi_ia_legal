import streamlit as st
import requests

# 1. ACCESO PARA TUS 5 USUARIOS
USUARIOS = {
    "admin": "clave777",
    "user1": "peru2026",
    "user2": "legal20",
    "user3": "pjia01",
    "user4": "estudio5"
}

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso P&JIA Core")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u in USUARIOS and USUARIOS[u] == p:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# 2. INTERFAZ PROFESIONAL
st.title("⚖️ P&JIA Core Pro")
st.subheader("Consultor Legal Especializado (Perú)")

# LIMPIEZA EXTREMA DE API KEY
# Obtenemos la clave y quitamos CUALQUER espacio, comilla o salto de línea
api_key = st.secrets.get("GROQ_API_KEY", "").strip().strip('"').strip("'").replace(" ", "").replace("\n", "").replace("\r", "")

if prompt := st.chat_input("Realice su consulta legal (Laboral, Civil o Penal)..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            if not api_key:
                st.error("Error: No se encontró la API Key en los Secrets.")
            else:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama3-70b-8192",
                    "messages": [
                        {"role": "system", "content": "Eres P&JIA Core, experto legal peruano. Cita leyes reales (DL 728, Código Civil/Penal). No inventes nada."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1
                }
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                data = response.json()
                
                if "choices" in data:
                    st.markdown(data["choices"][0]["message"]["content"])
                else:
                    st.error(f"Aviso del Sistema: {data.get('error', {}).get('message', 'Error desconocido')}")
        except Exception as e:
            st.error(f"Fallo técnico de conexión: {e}")
