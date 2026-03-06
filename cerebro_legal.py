import streamlit as st
import requests
from docx import Document
from io import BytesIO
import PyPDF2
from datetime import datetime, timedelta
import sqlite3
import pandas as pd

# 1. SISTEMA DE SEGURIDAD (5 Usuarios)
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

# 2. CONFIGURACIÓN E INICIALIZACIÓN
st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")
api_key = st.secrets.get("GROQ_API_KEY", "").strip().replace('"', '').replace("'", "")

def init_db():
    conn = sqlite3.connect('pjia_legal.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expedientes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, numero_exp TEXT, materia TEXT, 
                  contenido TEXT, resumen TEXT, fecha_registro TEXT, usuario TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. FUNCIONES TÉCNICAS
def extraer_texto_seguro(archivo):
    try:
        lector = PyPDF2.PdfReader(archivo)
        texto = ""
        for i in range(len(lector.pages[:100])): # Expandido a 100 páginas
            texto += lector.pages[i].extract_text() + "\n"
        if len(texto.strip()) < 100: return "ALERTA_ESCANEADO"
        return texto
    except: return "ERROR_LECTURA"

# 4. MENÚ LATERAL
with st.sidebar:
    st.title("⚖️ P&JIA Panel Pro")
    opcion = st.radio("Módulos:", [
        "Analista de Carpeta Fiscal (Tipicidad)", 
        "Búsqueda Global en Archivos", 
        "Gestor de Expedientes Guardados",
        "Agenda de Plazos Procesales",
        "Calculadora y Redacción"
    ])
    st.markdown("---")
    st.caption(f"Abogado: {st.session_state.user_actual}")

# 5. MÓDULO: ANALISTA DE CARPETA FISCAL (JURISTA INTEGRAL)
if opcion == "Analista de Carpeta Fiscal (Tipicidad)":
    st.title("🔍 Control de Tipicidad y Subsunción")
    st.info("Análisis experto basado en todo el ordenamiento jurídico peruano.")
    
    num_exp = st.text_input("Número de Carpeta/Caso:")
    archivo = st.file_uploader("Cargar Carpeta Fiscal (PDF)", type=["pdf"])
    
    if archivo and st.button("🚀 Iniciar Análisis Experto"):
        with st.spinner("Procesando expediente..."):
            texto_pdf = extraer_texto_seguro(archivo)
            
            if texto_pdf == "ALERTA_ESCANEADO":
                st.error("⚠️ El PDF es una imagen. Aplique OCR antes de subirlo.")
            else:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                
                # PROMPT SIN LIMITACIÓN DE ARTÍCULOS ESPECÍFICOS
                sys_prompt = """Eres P&JIA Core Pro, un jurista de élite peruano con dominio absoluto de:
                - Código Penal y Nuevo Código Procesal Penal.
                - Código Civil y Código Procesal Civil.
                - Nueva Ley Procesal del Trabajo y leyes laborales.
                
                TU MISIÓN: Analizar el documento adjunto. Si es una carpeta fiscal, realiza un juicio de SUBSUNCIÓN:
                1. ¿Los hechos encajan en los artículos del Código Penal citados? 
                2. Verifica elementos objetivos, subjetivos y de punibilidad.
                3. Identifica vicios procesales o falta de motivación.
                CITA LA NORMA EXACTA QUE CORRESPONDA AL CASO. No inventes artículos."""
                
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": f"DOCUMENTO:\n{texto_pdf[:35000]}"}
                    ], "temperature": 0.1
                }
                
                try:
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
                    analisis = res["choices"][0]["message"]["content"]
                    st.markdown(analisis)
                    
                    # Guardar
                    conn = sqlite3.connect('pjia_legal.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO expedientes (numero_exp, materia, contenido, resumen, fecha_registro, usuario) VALUES (?,?,?,?,?,?)",
                              (num_exp, "Penal", texto_pdf, analisis, datetime.now().strftime("%d/%m/%Y"), st.session_state.user_actual))
                    conn.commit()
                    conn.close()
                except: st.error("Error en la conexión con el servidor.")

# (Los demás módulos se mantienen con el conocimiento general del sistema)
