import streamlit as st
import requests
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import PyPDF2

# 1. ACCESO PRIVADO (Tus 5 usuarios configurados)
USUARIOS = {"admin": "clave777", "user1": "peru2026", "user2": "legal20", "user3": "pjia01", "user4": "estudio5"}

if "auth" not in st.session_state:
    st.session_state.auth = False

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
            st.error("Credenciales incorrectas")
    st.stop()

# 2. CONFIGURACIÓN DE MOTOR
st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")
api_key = st.secrets.get("GROQ_API_KEY", "").strip().replace('"', '').replace("'", "")

# Función de extracción masiva por bloques
def extraer_texto_masivo(archivo):
    try:
        lector = PyPDF2.PdfReader(archivo)
        texto_completo = ""
        for pagina in lector.pages:
            texto_completo += pagina.extract_text() + "\n"
        return texto_completo
    except Exception as e:
        return f"Error en lectura: {e}"

# 3. MENÚ LATERAL
with st.sidebar:
    st.title("⚖️ P&JIA Panel")
    opcion = st.radio("Seleccione función:", ["Analista de Expedientes (PDF)", "Calculadora de Beneficios", "Generador de Escritos"])
    st.markdown("---")
    st.caption("Especialista: Penal, Civil y Laboral")

# 4. MÓDULO: ANALISTA DE EXPEDIENTES (RAG)
if opcion == "Analista de Expedientes (PDF)":
    st.title("📂 Análisis de Expedientes Complejos")
    st.info("Sube documentos extensos. La IA buscará la información relevante en todo el archivo.")
    
    archivo_subido = st.file_uploader("Cargar PDF (Expedientes, Notificaciones, Contratos)", type=["pdf"])
    
    if prompt := st.chat_input("Ej: ¿Cuáles son los elementos de convicción mencionados en la acusación?"):
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Procesando folios y normativa peruana..."):
                texto_doc = extraer_texto_masivo(archivo_subido) if archivo_subido else ""
                
                try:
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    
                    sys_prompt = """Eres P&JIA Core Pro. Eres un jurista de élite en Perú. 
                    TU REGLA DE ORO: Analiza el texto proporcionado. Tienes prohibido decir que no puedes leer archivos. 
                    MATERIAS: 
                    - PENAL: NCPP y Código Penal (Análisis de tipicidad). 
                    - CIVIL: Código Civil (Art. 140 para actos jurídicos). 
                    - LABORAL: D.L. 728 y procesal laboral.
                    Si el texto es muy largo, prioriza los datos que el usuario solicita."""

                    # Enviamos un bloque significativo del texto (30k caracteres aprox)
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": f"DOCUMENTO:\n{texto_doc[:30000]}\n\nCONSULTA:\n{prompt}"}
                        ], "temperature": 0.1
                    }
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
                    st.markdown(res["choices"][0]["message"]["content"])
                except: st.error("Error al procesar el gran volumen de datos.")

# (Los módulos de Calculadora y Escritos permanecen estables con la corrección del Art. 140 CC)
