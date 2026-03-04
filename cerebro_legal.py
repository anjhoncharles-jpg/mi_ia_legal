import streamlit as st
import requests

# 1. CONFIGURACIÓN DE ACCESO (Tus 5 usuarios)
USUARIOS = {
    "admin": "clave777",
    "user1": "peru2026",
    "user2": "legal20",
    "user3": "pjia01",
    "user4": "estudio5"
}

# Inicialización de estado de autenticación
if "auth" not in st.session_state:
    st.session_state.auth = False

# Interfaz de Login
if not st.session_state.auth:
    st.set_page_config(page_title="Login P&JIA", page_icon="🔐")
    st.title("🔐 Acceso Privado P&JIA Core")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u in USUARIOS and USUARIOS[u] == p:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas. Intente de nuevo.")
    st.stop()

# 2. CONFIGURACIÓN DE LA INTERFAZ PRINCIPAL
st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")
st.title("⚖️ P&JIA Core Pro")
st.subheader("Consultor Legal Especializado (Perú)")
st.info("Especialidad: Derecho Laboral, Civil y Penal.")

# 3. GESTIÓN DE LA API KEY (Limpieza automática)
raw_key = st.secrets.get("GROQ_API_KEY", "")
# Limpiamos comillas, espacios y saltos de línea que causan el error "Invalid API Key"
api_key = raw_key.replace("\n", "").replace("\r", "").replace(" ", "").replace('"', '').replace("'", "").strip()

# 4. LÓGICA DEL CHAT
if prompt := st.chat_input("Realice su consulta legal..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            # Configuración de la petición a Groq
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.3-70b-versatile", # Modelo actualizado para evitar el error de 'decommissioned'
                "messages": [
                    {
                        "role": "system", 
                        "content": "Eres P&JIA Core, experto legal peruano. NO INVENTES LEYES. Usa estrictamente el D.L. 728, Código Civil 1984 y Código Penal. Si no conoces la respuesta exacta, indícalo."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            
            # Petición al servidor
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions", 
                headers=headers, 
                json=payload
            )
            
            res_json = response.json()
            
            # Manejo de la respuesta
            if "choices" in res_json:
                respuesta_ia = res_json["choices"][0]["message"]["content"]
                st.markdown(respuesta_ia)
            else:
                # Si Groq devuelve un error, lo mostramos de forma legible
                error_msg = res_json.get("error", {}).get("message", "Error desconocido de configuración.")
                st.error(f"Aviso del Sistema: {error_msg}")
                
        except Exception as e:
            st.error(f"Fallo técnico de conexión: {e}")

# Pie de página
st.markdown("---")
st.caption("P&JIA Core Pro - Sistema de Inteligencia Jurídica 2026")
