import streamlit as st
import requests
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import PyPDF2
from datetime import datetime, timedelta

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
            st.rerun()
        else: st.error("Credenciales incorrectas")
    st.stop()

# 2. CONFIGURACIÓN
st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")
api_key = st.secrets.get("GROQ_API_KEY", "").strip().replace('"', '').replace("'", "")

# Funciones de utilidad
def extraer_texto_masivo(archivo):
    lector = PyPDF2.PdfReader(archivo)
    return "\n".join([p.extract_text() for p in lector.pages])

# 3. MENÚ LATERAL
with st.sidebar:
    st.title("⚖️ P&JIA Panel")
    opcion = st.radio("Seleccione función:", [
        "Analista de Expedientes (PDF)", 
        "Agenda de Plazos Procesales",
        "Calculadora de Beneficios", 
        "Generador de Escritos"
    ])
    st.markdown("---")
    st.caption("Jurisprudencia y Asistencia IA 2026")

# 4. NUEVO MÓDULO: AGENDA DE PLAZOS PROCESALES
if opcion == "Agenda de Plazos Procesales":
    st.title("📅 Calculadora de Plazos Procesales")
    st.info("Calcula el vencimiento de plazos según la materia y la fecha de notificación.")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_notif = st.date_input("Fecha de Notificación:", datetime.now())
        materia = st.selectbox("Materia:", ["Penal (NCPP)", "Civil (CPC)", "Laboral (NLPT)"])
    
    with col2:
        tipo_plazo = st.selectbox("Tipo de Plazo:", [
            "Apelación de Auto (3 días)",
            "Apelación de Sentencia (5 días)",
            "Recurso de Casación (10 días)",
            "Contestación de Demanda (Vía Sumarísima - 5 días)",
            "Contestación de Demanda (Vía Abreviada - 10 días)"
        ])

    # Lógica de cálculo simple (días hábiles estimados)
    dias = 3 if "3 días" in tipo_plazo else 5 if "5 días" in tipo_plazo else 10
    vencimiento = fecha_notif + timedelta(days=dias)
    
    st.subheader(f"📌 Fecha estimada de vencimiento: {vencimiento.strftime('%d/%m/%Y')}")
    st.warning("Nota: Este cálculo es referencial. No olvide considerar feriados locales o judiciales específicos.")

# 5. MÓDULO: ANALISTA DE EXPEDIENTES (PDF)
elif opcion == "Analista de Expedientes (PDF)":
    st.title("📂 Análisis de Expedientes Complejos")
    archivo_subido = st.file_uploader("Cargar PDF", type=["pdf"])
    if prompt := st.chat_input("Consulta sobre el expediente..."):
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analizando..."):
                texto_doc = extraer_texto_masivo(archivo_subido) if archivo_subido else ""
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "Eres P&JIA Core Pro. Experto en Penal, Civil (Art. 140 CC) y Laboral. Analiza el documento sin excusas."},
                        {"role": "user", "content": f"DOCUMENTO:\n{texto_doc[:30000]}\n\nCONSULTA:\n{prompt}"}
                    ], "temperature": 0.1
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
                st.markdown(res["choices"][0]["message"]["content"])

# (Los módulos de Calculadora y Escritos se mantienen activos)
