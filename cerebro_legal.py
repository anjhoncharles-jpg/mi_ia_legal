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

# 2. CONFIGURACIÓN Y BASE DE DATOS
st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")
api_key = st.secrets.get("GROQ_API_KEY", "").strip().replace('"', '').replace("'", "")

def init_db():
    conn = sqlite3.connect('pjia_legal.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expedientes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  numero_exp TEXT, materia TEXT, contenido TEXT, 
                  fecha_registro TEXT, usuario TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. FUNCIONES DE APOYO
def extraer_texto_pdf(archivo):
    try:
        lector = PyPDF2.PdfReader(archivo)
        return "\n".join([p.extract_text() for p in lector.pages])
    except: return ""

def guardar_expediente(numero, materia, contenido):
    conn = sqlite3.connect('pjia_legal.db')
    c = conn.cursor()
    c.execute("INSERT INTO expedientes (numero_exp, materia, contenido, fecha_registro, usuario) VALUES (?,?,?,?,?)",
              (numero, materia, contenido, datetime.now().strftime("%Y-%m-%d %H:%M"), st.session_state.user_actual))
    conn.commit()
    conn.close()

# 4. MENÚ LATERAL
with st.sidebar:
    st.title("⚖️ P&JIA Panel")
    opcion = st.radio("Módulos:", [
        "Analista de Expedientes (PDF)", 
        "Gestor de Casos Guardados",
        "Agenda de Plazos Procesales",
        "Calculadora de Beneficios", 
        "Generador de Escritos"
    ])
    st.markdown("---")
    st.caption(f"Usuario: {st.session_state.user_actual}")

# 5. MÓDULO: ANALISTA Y CARGA
if opcion == "Analista de Expedientes (PDF)":
    st.title("📂 Analista y Registro de Expedientes")
    col_a, col_b = st.columns(2)
    with col_a:
        num_exp = st.text_input("Número de Expediente / Nombre del Caso")
        mat_exp = st.selectbox("Materia del Caso:", ["Penal", "Civil", "Laboral"])
    with col_b:
        archivo = st.file_uploader("Cargar PDF para Guardar", type=["pdf"])

    if st.button("💾 Guardar y Analizar"):
        if num_exp and archivo:
            texto = extraer_texto_pdf(archivo)
            guardar_expediente(num_exp, mat_exp, texto)
            st.success(f"Expediente {num_exp} guardado en la base de datos.")
            st.session_state.texto_analisis = texto
        else: st.warning("Complete el número de expediente y cargue el archivo.")

    if prompt := st.chat_input("Consulta sobre el expediente cargado..."):
        texto_para_ia = st.session_state.get("texto_analisis", "")
        with st.chat_message("assistant"):
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "Eres P&JIA Core Pro. Experto en Penal, Civil (Art. 140 CC) y Laboral. Analiza con rigor legal."},
                    {"role": "user", "content": f"DOCUMENTO:\n{texto_para_ia[:25000]}\n\nCONSULTA:\n{prompt}"}
                ], "temperature": 0.1
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
            st.markdown(res["choices"][0]["message"]["content"])

# 6. MÓDULO: GESTOR DE CASOS (CONSULTA DB)
elif opcion == "Gestor de Casos Guardados":
    st.title("🗃️ Archivo Digital P&JIA")
    conn = sqlite3.connect('pjia_legal.db')
    df = pd.read_sql_query("SELECT id, numero_exp, materia, fecha_registro, usuario FROM expedientes", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        id_selec = st.number_input("Ingrese ID para re-analizar contenido:", min_value=int(df['id'].min()), max_value=int(df['id'].max()))
        if st.button("Cargar para Análisis"):
            conn = sqlite3.connect('pjia_legal.db')
            c = conn.cursor()
            c.execute("SELECT contenido FROM expedientes WHERE id=?", (id_selec,))
            st.session_state.texto_analisis = c.fetchone()[0]
            conn.close()
            st.info("Contenido cargado. Vaya al módulo 'Analista' para chatear con este documento.")
    else: st.write("No hay expedientes guardados aún.")

# (Los demás módulos de Plazos, Calculadora y Escritos se mantienen iguales)
elif opcion == "Agenda de Plazos Procesales":
    st.title("📅 Calculadora de Plazos")
    f_notif = st.date_input("Fecha de Notificación:")
    tipo = st.selectbox("Recurso:", ["Apelación Auto (3 días)", "Apelación Sentencia (5 días)", "Casación (10 días)"])
    dias = 3 if "3" in tipo else 5 if "5" in tipo else 10
    st.subheader(f"Vencimiento: {(f_notif + timedelta(days=dias)).strftime('%d/%m/%Y')}")

elif opcion == "Calculadora de Beneficios":
    st.title("🧮 Beneficios Sociales")
    sueldo = st.number_input("Sueldo", min_value=1025.0)
    meses = st.slider("Meses", 1, 12)
    st.metric("Total Estimado", f"S/. {(sueldo * meses / 6):,.2f}") # Cálculo resumido

elif opcion == "Generador de Escritos":
    st.title("📝 Redacción Jurídica")
    tipo_e = st.text_input("Tipo de Escrito (ej. Contestación Penal)")
    hechos = st.text_area("Hechos del caso")
    if st.button("Generar"):
        st.write("Generando borrador formal...")
