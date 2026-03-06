import streamlit as st
import requests
import PyPDF2
import docx
import pandas as pd
from io import BytesIO
import pytesseract
from pdf2image import convert_from_bytes
import sqlite3
from datetime import datetime

# 1. CONFIGURACIÓN E IA
st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")
api_key = st.secrets.get("GROQ_API_KEY", "").strip()

# 2. MOTOR DE LECTURA ROBUSTO
def leer_carpeta_fiscal(archivo):
    ext = archivo.name.split('.')[-1].lower()
    texto = ""
    try:
        if ext == "pdf":
            contenido = archivo.read()
            # Intento 1: Texto Digital
            lector = PyPDF2.PdfReader(BytesIO(contenido))
            for p in lector.pages[:15]: # Limite de páginas para velocidad
                texto += p.extract_text() or ""
            
            # Intento 2: OCR (Si el texto es muy corto)
            if len(texto.strip()) < 100:
                st.info("🔄 Documento escaneado detectado. Iniciando OCR en español...")
                # Procesamos solo las primeras 10 páginas para evitar saturar el servidor
                paginas_img = convert_from_bytes(contenido, first_page=1, last_page=10)
                for img in paginas_img:
                    texto += pytesseract.image_to_string(img, lang='spa')
        
        elif ext in ["docx", "doc"]:
            doc = docx.Document(archivo)
            texto = "\n".join([p.text for p in doc.paragraphs])
            
        elif ext in ["xlsx", "xls"]:
            df = pd.read_excel(archivo)
            texto = df.to_string()

        return texto
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return None

# 3. INTERFAZ DE ANÁLISIS
st.title("🔍 Analista de Carpeta Fiscal")
archivo_legal = st.file_uploader("Cargar Carpeta Fiscal (PDF/Word/Excel)", type=["pdf", "docx", "xlsx"])

if archivo_legal and st.button("🚀 Iniciar Análisis de Tipicidad"):
    with st.spinner("Extrayendo datos y analizando subsunción..."):
        texto_final = leer_carpeta_fiscal(archivo_legal)
        
        if texto_final:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            sys_prompt = "Eres un jurista de élite peruano. Realiza un control de tipicidad. Compara los hechos con el Código Penal y Procesal Penal. Detecta errores en la imputación fiscal."
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": f"CARPETA FISCAL:\n{texto_final[:25000]}"}
                ], "temperature": 0.1
            }
            
            try:
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
                st.subheader("📋 Dictamen de Tipicidad")
                st.markdown(res["choices"][0]["message"]["content"])
            except:
                st.error("La IA está saturada, intenta de nuevo en un momento.")
