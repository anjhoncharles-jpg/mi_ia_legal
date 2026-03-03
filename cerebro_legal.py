import streamlit as st
import os
import requests
from docx import Document
from io import BytesIO

# 1. CONFIGURACIÓN DE USUARIOS (Tus 5 accesos privados)
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
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("Error: No se encontró la API_KEY en Secrets.")
    st.stop()

st.set_page_config(page_title="P&JIA Core", page_icon="⚖️")
st.title("⚖️ P&JIA Core - Inteligencia Legal")
st.subheader("Especialista en Derecho Laboral, Civil y Penal (Perú)")

# Barra lateral para utilidades
with st.sidebar:
    st.header("Herramientas")
    archivo_subido = st.file_uploader("Subir documento para análisis (PDF/Texto)", type=['pdf', 'txt'])
    if st.button("Limpiar Chat"):
        st.session_state.messages = []
        st.rerun()

# Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("Escribe tu consulta legal aquí..."):
    # Si hay un archivo subido, lo mencionamos en el contexto
    contexto_archivo = ""
    if archivo_subido:
        contexto_archivo = f"\n[Contexto del archivo subido: {archivo_subido.name}]"
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta de la IA con el Prompt Maestro especializado
    with st.chat_message("assistant"):
        with st.spinner("Analizando base legal peruana..."):
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama3-70b-8192", # Usamos el modelo más potente
                        "messages": [
                            {
                                "role": "system", 
                                "content": (
                                    "Eres P&JIA Core, una IA de nivel superior experta en Derecho Peruano. "
                                    "NORMAS DE CONDUCTA: "
                                    "1. NO INVENTAR artículos ni leyes. Cita la normativa exactamente como está redactada. "
                                    "2. LABORAL: Usa D.L. 728, Ley 29783, y normas de SUNAFIL. "
                                    "3. CIVIL: Usa el Código Civil de 1984 y el Código Procesal Civil. "
                                    "4. PENAL: Usa el Código Penal y Código Procesal Penal de 2004. "
                                    "5. RESPUESTA: Base Legal, Análisis Jurídico y Recomendación Estratégica."
                                )
                            },
                            {"role": "user", "content": prompt + contexto_archivo}
                        ],
                        "temperature": 0.1 # Precisión máxima
                    }
                )
                
                res_json = response.json()
                full_response = res_json["choices"][0]["message"]["content"]
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Generador de Word corregido
                doc = Document()
                doc.add_heading('P&JIA Core - Informe Jurídico', 0)
                doc.add_paragraph(full_response)
                bio = BytesIO()
                doc.save(bio)
                
                st.download_button(
                    label="📥 Descargar Respuesta en Word",
                    data=bio.getvalue(),
                    file_name="consulta_legal_pjia.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error("Hubo un error en la consulta. Verifica tu API KEY en Secrets.")
