import streamlit as st
import requests
import PyPDF2
import docx
import pandas as pd
from pptx import Presentation
from io import BytesIO
from datetime import datetime
import sqlite3
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")
api_key = st.secrets.get("GROQ_API_KEY", "").strip().replace('"', '').replace("'", "")

# 2. SISTEMA DE ACCESO
USUARIOS = {"admin": "clave777", "user1": "peru2026"}
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso Privado P&JIA")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u in USUARIOS and USUARIOS[u] == p:
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. MOTOR DE LECTURA UNIVERSAL (CON PROTECCIÓN DE ERRORES)
def leer_archivo_universal(archivo):
    ext = archivo.name.split('.')[-1].lower()
    texto = ""
    try:
        if ext == "pdf":
            archivo_bytes = archivo.read()
            # Intento 1: Texto digital
            lector = PyPDF2.PdfReader(BytesIO(archivo_bytes))
            for p in lector.pages[:20]: # Primeras 20 páginas para rapidez
                texto += p.extract_text() or ""
            
            # Intento 2: OCR si es imagen
            if len(texto.strip()) < 100:
                st.warning("🔄 Detectado PDF escaneado. Iniciando OCR...")
                imagenes = convert_from_bytes(archivo_bytes, first_page=1, last_page=5)
                for img in imagenes:
                    texto += pytesseract.image_to_string(img, lang='spa')
        
        elif ext in ["docx", "doc"]:
            doc = docx.Document(archivo)
            texto = "\n".join([p.text for p in doc.paragraphs])
        
        elif ext in ["xlsx", "xls"]:
            df = pd.read_excel(archivo)
            texto = df.to_string()
            
    except Exception as e:
        st.error(f"Error al procesar: {e}. Asegúrate de tener 'packages.txt' configurado.")
    return texto

# 4. INTERFAZ
with st.sidebar:
    st.title("⚖️ P&JIA Panel")
    opcion = st.radio("Módulos:", ["Analista de Carpeta Fiscal", "Búsqueda Global"])

if opcion == "Analista de Carpeta Fiscal":
    st.title("🔍 Análisis de Tipicidad")
    archivo = st.file_uploader("Cargar Carpeta Fiscal", type=["pdf", "docx", "xlsx"])
    
    if archivo and st.button("🚀 Iniciar Análisis"):
        with st.spinner("Procesando..."):
            texto = leer_archivo_universal(archivo)
            if texto:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "Eres un jurista experto en derecho penal, civil y laboral peruano. Realiza un control de tipicidad fáctica y jurídica."},
                        {"role": "user", "content": f"Analiza este documento y detecta errores en la tipificación fiscal:\n\n{texto[:25000]}"}
                    ], "temperature": 0.1
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
                st.markdown(res["choices"][0]["message"]["content"])
