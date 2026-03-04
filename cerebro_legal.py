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

# LIMPIEZA AUTOMÁTICA DE API KEY
raw_key = st.secrets.get("GROQ_API_KEY", "")
# Esta línea borra espacios, comillas y saltos de línea que causan el error
api_key = raw_key.replace("\n", "").replace("\r", "").replace(" ", "").replace('"', '').replace("'", "").strip()

if prompt := st.chat_input("Realice su consulta legal (Laboral, Civil o Penal)..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama3-70b-8192",
                "messages": [
                    {
                        "role": "system", 
                        "content": "Eres P&JIA Core. Experto legal peruano. NO INVENTES LEYES. Usa estrictamente el D.L. 728, Código Civil 1984 y Código Penal. Estructura: Base Legal, Análisis, Conclusión."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            data = response.json()
            
            if "choices" in data:
                st.markdown(data["choices"][0]["message"]["content"])
            else:
                msg = data.get("error", {}).get("message", "Error de configuración")
                st.error(f"Aviso del Sistema: {msg}")
        except Exception as e:
            st.error(f"Fallo de conexión: {e}")
