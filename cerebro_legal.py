import streamlit as st
import requests

# Configuración básica
st.set_page_config(page_title="P&JIA Core", page_icon="⚖️")

# 1. LOGIN SIMPLE
USUARIOS = {"admin": "clave777", "user1": "peru2026"}

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso P&JIA")
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u] == p:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Incorrecto")
    st.stop()

# 2. INTERFAZ DE IA
st.title("⚖️ P&JIA Core Pro")
api_key = st.secrets.get("GROQ_API_KEY", "").strip() # Quitamos espacios o saltos invisibles

if prompt := st.chat_input("Consulta legal peruana..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            # Quitamos cualquier salto de línea que pueda venir de la clave
            clean_key = api_key.replace("\n", "").replace("\r", "").strip()
            
            headers = {"Authorization": f"Bearer {clean_key}", "Content-Type": "application/json"}
            data = {
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "Eres P&JIA Core, experto legal peruano. Cita leyes reales (DL 728, Código Civil/Penal)."},
                    {"role": "user", "content": prompt}
                ]
            }
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
            res = r.json()
            
            if "choices" in res:
                respuesta = res["choices"][0]["message"]["content"]
                st.markdown(respuesta)
            else:
                st.error(f"Error de API: {res.get('error', {}).get('message', 'Clave mal configurada')}")
        except Exception as e:
            st.error(f"Error técnico: {e}")
