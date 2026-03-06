import streamlit as st
import requests
import PyPDF2
import docx
import pandas as pd
from pptx import Presentation
from io import BytesIO
from datetime import datetime, timedelta
import sqlite3
import pytesseract
from pdf2image import convert_from_bytes
import numpy as np
from PIL import Image

# 1. SEGURIDAD Y ACCESO
USUARIOS = {"admin": "clave777", "user1": "peru2026", "user2": "legal20", "user3": "pjia01", "user4": "estudio5"}
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.set_page_config(page_title="Login P&JIA", page_icon="🔐")
    st.title("🔐 Acceso Privado P&JIA Core")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u in USUARIOS and USUARIOS[u] == p:
            st.session_state.auth = True
            st.session_state.user_actual = u
            st.rerun()
        else: st.error("Credenciales incorrectas")
    st.stop()

# 2. CONFIGURACIÓN GLOBAL
st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")
api_key = st.secrets.get("GROQ_API_KEY", "").strip().replace('"', '').replace("'", "")

# Inicializar Base de Datos
def init_db():
    conn = sqlite3.connect('pjia_legal.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expedientes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, numero_exp TEXT, materia TEXT, 
                  contenido TEXT, resumen TEXT, fecha_registro TEXT, usuario TEXT)''')
    conn.commit()
    conn.close()
init_db()

# 3. MOTORES DE LECTURA UNIVERSAL
def leer_archivo(archivo):
    ext = archivo.name.split('.')[-1].lower()
    texto = ""
    
    if ext == "pdf":
        pdf_bytes = archivo.read()
        lector = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        for p in lector.pages[:50]:
            texto += p.extract_text() or ""
        # Si está vacío o es imagen, aplicar OCR
        if len(texto.strip()) < 100:
            st.info("Detectado PDF escaneado. Iniciando OCR (esto puede tardar)...")
            imagenes = convert_from_bytes(pdf_bytes, first_page=1, last_page=10)
            for img in imagenes:
                texto += pytesseract.image_to_string(img)
                
    elif ext in ["docx", "doc"]:
        doc = docx.Document(archivo)
        texto = "\n".join([p.text for p in doc.paragraphs])
        
    elif ext in ["xlsx", "xls"]:
        df = pd.read_excel(archivo)
        texto = f"CONTENIDO DE EXCEL:\n{df.to_string()}"
        
    elif ext == "pptx":
        prs = Presentation(archivo)
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    texto += shape.text + "\n"
                    
    elif ext in ["jpg", "png", "jpeg"]:
        img = Image.open(archivo)
        texto = pytesseract.image_to_string(img)
        
    return texto

# 4. INTERFAZ Y LÓGICA
with st.sidebar:
    st.title("⚖️ P&JIA Panel")
    opcion = st.radio("Módulos:", ["Analista Universal", "Búsqueda Global", "Gestor de Archivo", "Agenda de Plazos"])

if opcion == "Analista Universal":
    st.title("📂 Análisis de Documentos y Carpeta Fiscal")
    st.write("Sube cualquier archivo (PDF, Word, Excel, PPT o Foto) para control de tipicidad y análisis legal.")
    
    num_exp = st.text_input("Identificador del Caso/Expediente:")
    archivo = st.file_uploader("Cargar documento", type=["pdf", "docx", "xlsx", "pptx", "jpg", "png"])
    
    if archivo and st.button("🚀 Iniciar Análisis Experto"):
        with st.spinner("Procesando y aplicando IA Jurídica..."):
            texto_extraido = leer_archivo(archivo)
            
            if len(texto_extraido) < 10:
                st.error("No se pudo extraer texto. El archivo podría estar protegido o dañado.")
            else:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                sys_prompt = "Eres P&JIA Core Pro. Analiza el documento con base en toda la normativa peruana (Civil, Penal, Laboral). Si es penal, realiza control de tipicidad fáctica y jurídica. No inventes artículos, cita la ley exacta."
                
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": f"CONTENIDO:\n{texto_extraido[:30000]}"}
                    ], "temperature": 0.1
                }
                
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
                analisis = res["choices"][0]["message"]["content"]
                
                st.subheader("📋 Resultado del Análisis")
                st.markdown(analisis)
                
                # Guardar en DB
                conn = sqlite3.connect('pjia_legal.db')
                c = conn.cursor()
                c.execute("INSERT INTO expedientes (numero_exp, materia, contenido, resumen, fecha_registro, usuario) VALUES (?,?,?,?,?,?)",
                          (num_exp, "Multidisciplinario", texto_extraido[:50000], analisis, datetime.now().strftime("%d/%m/%Y"), st.session_state.user_actual))
                conn.commit()
                conn.close()

# 5. MÓDULOS RESTANTES (Búsqueda, Gestor, Agenda)
# (Se mantienen con la lógica de búsqueda en la base de datos SQL para encontrar palabras clave)
