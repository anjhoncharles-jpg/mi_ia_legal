import streamlit as st
import requests
from docx import Document
from io import BytesIO
import PyPDF2
from datetime import datetime
import sqlite3
import pandas as pd

# 1. SISTEMA DE ACCESO
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

# 2. CONFIGURACIÓN Y BASE DE DATOS
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

# 3. LECTURA DE PDF ROBUSTA
def extraer_texto_seguro(archivo):
    try:
        lector = PyPDF2.PdfReader(archivo)
        texto = ""
        # Leemos hasta 50 páginas para capturar la imputación fiscal completa
        for i in range(len(lector.pages[:50])):
            texto += lector.pages[i].extract_text() + "\n"
        
        if len(texto.strip()) < 100:
            return "ALERTA_ESCANEADO"
        return texto
    except Exception as e:
        return f"ERROR_LECTURA: {e}"

# 4. MENÚ LATERAL
with st.sidebar:
    st.title("⚖️ P&JIA Panel")
    opcion = st.radio("Módulos:", ["Analista de Carpeta Fiscal", "Búsqueda Global", "Gestor de Archivo"])
    st.markdown("---")
    st.info(f"Usuario: {st.session_state.user_actual}")

# 5. MÓDULO: ANALISTA DE CARPETA FISCAL (CONTROL DE TIPICIDAD)
if opcion == "Analista de Carpeta Fiscal":
    st.title("🔍 Control de Tipicidad - Carpeta Fiscal")
    st.markdown("Sube la disposición fiscal para verificar si la subsunción de los delitos es correcta.")
    
    num_exp = st.text_input("Número de Carpeta Fiscal / Caso")
    archivo = st.file_uploader("Cargar Carpeta Fiscal (PDF)", type=["pdf"])
    
    if archivo:
        if st.button("🚀 Iniciar Análisis de Tipicidad"):
            with st.spinner("Analizando hechos y normas penales..."):
                texto_extraido = extraer_texto_seguro(archivo)
                
                if texto_extraido == "ALERTA_ESCANEADO":
                    st.error("⚠️ El PDF parece ser una imagen/escaneado. El sistema no puede extraer texto de fotos aún. Intenta con un PDF digital.")
                else:
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    
                    sys_prompt = """Eres un experto en Derecho Penal peruano. Tu misión es el CONTROL DE LEGALIDAD.
                    1. Analiza los HECHOS narrados por la Fiscalía.
                    2. Contrasta si esos hechos cumplen con todos los elementos del TIPO PENAL imputado (Sujeto, conducta, dolo, etc.).
                    3. Si hay falta de elementos de convicción o error en la tipificación, indica 'ERROR DE SUBSUNCIÓN' o 'ATIPICIDAD'.
                    4. Cita siempre el Código Penal y el NCPP.
                    5. Sé crítico. Si la Fiscal ha tipificado mal, explica por qué."""

                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": f"TEXTO DE LA CARPETA:\n{texto_extraido[:30000]}\n\nRealiza un análisis detallado de la tipificación."}
                        ], "temperature": 0.1
                    }
                    
                    try:
                        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
                        analisis = res["choices"][0]["message"]["content"]
                        st.session_state.ultimo_analisis = analisis
                        st.success("Análisis Completo")
                        st.markdown(analisis)
                        
                        # Guardar automáticamente en la DB
                        conn = sqlite3.connect('pjia_legal.db')
                        c = conn.cursor()
                        c.execute("INSERT INTO expedientes (numero_exp, materia, contenido, resumen, fecha_registro, usuario) VALUES (?,?,?,?,?,?)",
                                  (num_exp, "Penal", texto_extraido, analisis, datetime.now().strftime("%d/%m/%Y"), st.session_state.user_actual))
                        conn.commit()
                        conn.close()
                    except:
                        st.error("Error al conectar con el motor de IA.")

# 6. MÓDULO: BÚSQUEDA GLOBAL
elif opcion == "Búsqueda Global":
    st.title("🔎 Buscador P&JIA")
    query = st.text_input("Buscar en todos los expedientes guardados (Nombres, DNI, Delitos):")
    if query:
        conn = sqlite3.connect('pjia_legal.db')
        df = pd.read_sql_query(f"SELECT numero_exp, materia, fecha_registro FROM expedientes WHERE contenido LIKE '%{query}%' OR resumen LIKE '%{query}%'", conn)
        conn.close()
        if not df.empty: st.table(df)
        else: st.warning("No se encontraron coincidencias.")

# 7. MÓDULO: GESTOR DE ARCHIVO
elif opcion == "Gestor de Archivo":
    st.title("🗃️ Archivo Digital")
    conn = sqlite3.connect('pjia_legal.db')
    df = pd.read_sql_query("SELECT id, numero_exp, materia, fecha_registro FROM expedientes", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)
