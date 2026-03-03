import streamlit as st
import requests

# 1. CONFIGURACIÓN DE USUARIOS
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

# 2. INTERFAZ Y LÓGICA DE IA
st.title("⚖️ P&JIA Core Pro")
st.subheader("Especialista Legal Perú")

# FUNCIÓN CRÍTICA: Limpiar la clave de espacios, comillas o saltos de línea
def limpiar_clave(key):
    return key.replace('"', '').replace("'", "").replace(" ", "").strip()

raw_key = st.secrets.get("GROQ_API_KEY", "")
api_key = limpiar_clave(raw_key)

if prompt := st.chat_input("Consulta legal peruana..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "Eres P&JIA Core, experto legal peruano. Cita leyes reales (DL 728, Código Civil/Penal). No inventes nada."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            res = r.json()
            
            if "choices" in res:
                st.markdown(res["choices"][0]["message"]["content"])
            else:
                msg = res.get("error", {}).get("message", "Error de configuración")
                st.error(f"Error de la IA: {msg}")
        except Exception as e:
            st.error(f"Error técnico: {e}")
