import streamlit as st
import requests
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import PyPDF2
from datetime import datetime, timedelta
import sqlite3
import pandas as pd

# 1. ACCESO PRIVADO
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

# 2. CONFIGURACIÓN Y DB
st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")
api_key = st.secrets.get("GROQ_API_KEY", "").strip().replace('"', '').replace("'", "")

def init_db():
    conn = sqlite3.connect('pjia_legal.db')
    c = conn.cursor()
    # Añadimos la columna 'resumen' a la tabla
    c.execute('''CREATE TABLE IF NOT EXISTS expedientes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  numero_exp TEXT, materia TEXT, contenido TEXT, 
                  resumen TEXT, fecha_registro TEXT, usuario TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. LÓGICA DE INTELIGENCIA JURÍDICA
def generar_resumen_ia(texto, materia):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt_sistema = f"Eres un experto en Derecho {materia} peruano. Resume este documento en 3 puntos: 1. Hechos relevantes, 2. Base legal detectada (Cita Art. 140 CC si es civil, NCPP si es penal o DL 728 si es laboral), 3. Riesgos procesales."
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"Documento: {texto[:15000]}"}
        ], "temperature": 0.2
    }
    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
        return res["choices"][0]["message"]["content"]
    except: return "Resumen no disponible por error de conexión."

# 4. MENÚ LATERAL
with st.sidebar:
    st.title("⚖️ P&JIA Panel")
    opcion = st.radio("Módulos:", ["Analista de Expedientes (PDF)", "Gestor de Casos Guardados", "Agenda de Plazos", "Calculadora Laboral", "Generador de Escritos"])
    st.markdown("---")
    st.caption(f"Conectado como: {st.session_state.user_actual}")

# 5. MÓDULO: ANALISTA (CON AUTO-RESUMEN)
if opcion == "Analista de Expedientes (PDF)":
    st.title("📂 Registro y Análisis de Casos")
    col1, col2 = st.columns(2)
    with col1:
        num_exp = st.text_input("Número de Expediente")
        mat_exp = st.selectbox("Materia:", ["Penal", "Civil", "Laboral"])
    with col2:
        archivo = st.file_uploader("Subir PDF", type=["pdf"])

    if st.button("💾 Guardar y Generar Resumen"):
        if num_exp and archivo:
            with st.spinner("Procesando documento..."):
                texto = "\n".join([p.extract_text() for p in PyPDF2.PdfReader(archivo).pages])
                resumen = generar_resumen_ia(texto, mat_exp)
                
                conn = sqlite3.connect('pjia_legal.db')
                c = conn.cursor()
                c.execute("INSERT INTO expedientes (numero_exp, materia, contenido, resumen, fecha_registro, usuario) VALUES (?,?,?,?,?,?)",
                          (num_exp, mat_exp, texto, resumen, datetime.now().strftime("%d/%m/%Y"), st.session_state.user_actual))
                conn.commit()
                conn.close()
                
                st.success("Expediente guardado exitosamente.")
                st.subheader("📝 Resumen Ejecutivo Automático")
                st.markdown(resumen)
        else: st.warning("Por favor, ingrese el número y el archivo.")

# 6. MÓDULO: GESTOR DE CASOS (PARA VER RESÚMENES)
elif opcion == "Gestor de Casos Guardados":
    st.title("🗃️ Archivo Digital P&JIA")
    conn = sqlite3.connect('pjia_legal.db')
    df = pd.read_sql_query("SELECT id, numero_exp, materia, resumen, fecha_registro FROM expedientes", conn)
    conn.close()
    
    if not df.empty:
        for idx, row in df.iterrows():
            with st.expander(f"📁 Caso: {row['numero_exp']} - {row['materia']} ({row['fecha_registro']})"):
                st.write("**Resumen de la IA:**")
                st.markdown(row['resumen'])
                if st.button(f"Analizar a fondo ID {row['id']}"):
                    st.info("Cargando contenido para el chat...")
                    # Lógica para cargar texto en sesión y chatear
    else: st.write("Aún no hay expedientes registrados.")

# Los demás módulos se mantienen operativos para asegurar el flujo de trabajo
