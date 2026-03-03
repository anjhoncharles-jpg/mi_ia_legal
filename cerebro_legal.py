import streamlit as st
import requests

# 1. Configuración de Usuarios
USUARIOS = {"admin": "clave777", "user1": "peru2026", "user2": "legal20", "user3": "pjia01", "user4": "estudio5"}

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso P&JIA")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u in USUARIOS and USUARIOS[u] == p:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# 2. Interfaz Principal
st.title("⚖️ P&JIA Core Pro")
st.subheader("Especialista Legal Perú")

# Limpieza automática de la clave API
raw_key = st.secrets.get("GROQ_API_KEY", "")
api_key = raw_key.replace("\n", "").replace("\r", "").replace(" ", "").strip()

if prompt := st.chat_input("Consulta legal peruana..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "Eres P&JIA Core. Experto legal peruano. No inventes leyes. Cita D.L. 728, Código Civil y Penal."},
                    {"role": "user", "content": prompt}
                ]
            }
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
            res_json = response.json()
            
            if "choices" in res_json:
                st.markdown(res_json["choices"][0]["message"]["content"])
            else:
                st.error(f"Error de API: {res_json.get('error', {}).get('message', 'Clave inválida')}")
        except Exception as e:
            st.error(f"Fallo de conexión: {e}")
