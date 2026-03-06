import streamlit as st
import requests
from docx import Document
from io import BytesIO
import PyPDF2
from datetime import datetime
import sqlite3
import pandas as pd

# 1. ACCESO Y CONFIGURACIÓN
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
    st.stop()

st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")
api_key = st.secrets.get("GROQ_API_KEY", "").strip().replace('"', '').replace("'", "")

# 2. BASE DE DATOS E INTELIGENCIA
def init_db():
    conn = sqlite3.connect('pjia_legal.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expedientes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, numero_exp TEXT, materia TEXT, 
                  contenido TEXT, resumen TEXT, fecha_registro TEXT, usuario TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. MENÚ LATERAL
with st.sidebar:
    st.title("⚖️ P&JIA Panel")
    opcion = st.radio("Módulos:", ["Analista de Carpeta Fiscal", "Búsqueda Global", "Gestor de Archivo", "Calculadora y Escritos"])
    st.markdown("---")
    st.info("Especialidad: Control de Tipicidad y Análisis de Subsunción.")

# 4. MÓDULO: ANALISTA DE CARPETA FISCAL (CONTROL DE TIPICIDAD)
if opcion == "Analista de Carpeta Fiscal":
    st.title("🔍 Control de Tipicidad y Subsunción Fiscal")
    st.warning("Sube la Carpeta Fiscal para verificar si los delitos han sido correctamente tipificados.")
    
    archivo = st.file_uploader("Cargar Carpeta Fiscal (PDF)", type=["pdf"])
    
    if archivo:
        if st.button("Analizar Tipicidad"):
            with st.spinner("Evaluando elementos del tipo penal..."):
                texto = "\n".join([p.extract_text() for p in PyPDF2.PdfReader(archivo).pages])
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                
                # PROMPT ESPECÍFICO PARA CONTROL FISCAL
                sys_prompt = """Eres un experto en Derecho Penal y Procesal Penal peruano (NCPP). 
                Tu tarea es realizar un CONTROL DE TIPICIDAD. 
                1. Analiza los hechos descritos en el PDF.
                2. Contrasta los hechos con los delitos tipificados por la Fiscalía.
                3. Determina si falta algún elemento del tipo (Sujeto, Objeto, Conducta, Dolo/Culpa).
                4. Cita artículos específicos del Código Penal.
                Si encuentras que un hecho NO se subsume en el delito, indícalo como ATIPICIDAD."""

                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": f"CARPETA FISCAL:\n{texto[:25000]}"}
                    ], "temperature": 0.1
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
                st.session_state.analisis_fiscal = res["choices"][0]["message"]["content"]
                st.markdown(st.session_state.analisis_fiscal)

# 5. MÓDULO: BÚSQUEDA GLOBAL
elif opcion == "Búsqueda Global":
    st.title("🔎 Buscador Maestro P&JIA")
    query = st.text_input("Ingresa nombre, DNI o palabra clave a buscar en toda tu base de datos:")
    
    if query:
        conn = sqlite3.connect('pjia_legal.db')
        # Buscamos en el contenido de todos los PDFs guardados
        df = pd.read_sql_query(f"SELECT numero_exp, materia, fecha_registro FROM expedientes WHERE contenido LIKE '%{query}%' OR resumen LIKE '%{query}%'", conn)
        conn.close()
        
        if not df.empty:
            st.success(f"Se encontraron {len(df)} coincidencias:")
            st.table(df)
        else:
            st.error("No se encontraron registros con esa información.")

# (Los demás módulos de Gestión y Calculadora se mantienen simplificados para el flujo)
