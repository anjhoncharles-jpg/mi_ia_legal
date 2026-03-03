import streamlit as st
import requests

# Configuración básica
st.set_page_config(page_title="P&JIA Core", page_icon="⚖️")

# 1. LOGIN
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

# 2. INTERFAZ
st.title("⚖️ P&JIA Core Pro")
st.subheader("Especialista Legal Perú")

# Obtenemos y LIMPIAMOS la clave de cualquier espacio o salto de línea
raw_key = st.secrets.get("GROQ_API_KEY", "")
api_key = raw_key.replace("\n", "").replace("\r", "").replace(" ", "").strip()

if prompt := st.chat_input("Consulta legal peruana..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama3-70b-8192",
                "messages": [
                    {
                        "role": "system", 
                        "content": "Eres P&JIA Core, experto legal peruano. Cita leyes reales como el D.L. 728, Código Civil y Penal. No inventes artículos."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
            res_json = response.json()
            
            if "choices" in res_json:
                respuesta = res_json["choices"][0]["message"]["content"]
                st.markdown(respuesta)
            else:
                error_info = res_json.get("error", {}).get("message", "Error de configuración")
                st.error(f"Error de la IA: {error_info}")
                
        except Exception as e:
            st.error(f"Fallo de conexión: {e}")
