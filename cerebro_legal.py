import streamlit as st
import os
import requests
from docx import Document
from io import BytesIO

# 1. CONFIGURACIÓN DE USUARIOS (Máximo 5)
USUARIOS_PERMITIDOS = {
    "admin": "clave777",
    "user1": "peru2026",
    "user2": "legal20",
    "user3": "pjia01",
    "user4": "estudio5"
}

# 2. FUNCIÓN DE LOGIN
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.set_page_config(page_title="Login P&JIA", page_icon="🔐")
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

# --- CONFIGURACIÓN DE LA IA (DESPUÉS DEL LOGIN) ---

# Obtener la API Key desde los Secrets de Streamlit
API_KEY = st.secrets["GROQ_API_KEY"]

st.title("⚖️ P&JIA Core - Especialista Legal Perú")
st.markdown("---")

# Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("Escribe tu consulta legal (Civil, Laboral o Penal)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Llamada a la IA con el "Cerebro Legal" (Instrucciones de no inventar leyes)
    with st.chat_message("assistant"):
        with st.spinner("Consultando base legal..."):
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama3-8b-8192",
                        "messages": [
                            {
                                "role": "system", 
                                "content": (
                                    "Eres P&JIA Core, una IA experta en Derecho Peruano. "
                                    "IMPORTANTE: No inventes artículos ni leyes. Cita las normas exactamente como son. "
                                    "Si es Laboral: usa el D.L. 728. Si es Civil: Código Civil de 1984. "
                                    "Si es Penal: Código Penal vigente. "
                                    "Estructura: 1. Base Legal, 2. Análisis, 3. Conclusión."
                                )
                            },
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2 # Baja temperatura para mayor precisión
                    }
                )
                
                full_response = response.json()["choices"][0]["message"]["content"]
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Botón para descargar en Word
                doc = Document()
                doc.add_heading('Informe Legal - P&JIA Core', 0)
                doc.add_paragraph(full_response)
                bio = BytesIO()
                doc.save(bio)
                
                st.download_button(
                    label="📥 Descargar Informe en Word",
                    data=bio.getvalue(),
                    file_name="informe_legal.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error(f"Error de conexión: {e}")
