import streamlit as st
import requests
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import PyPDF2
from datetime import datetime, timedelta

# 1. ACCESO PRIVADO (Tus 5 usuarios)
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

# Función para extraer texto de archivos grandes
def extraer_texto_pdf(archivo):
    try:
        lector = PyPDF2.PdfReader(archivo)
        texto = ""
        for pagina in lector.pages:
            texto += pagina.extract_text() + "\n"
        return texto
    except: return "Error al leer el PDF."

# Función para Word con Logo P&JIA
def crear_word_profesional(titulo, contenido):
    doc = Document()
    header = doc.sections[0].header
    header.paragraphs[0].text = "P&JIA - CONSULTORES LEGALES\nEspecialistas en Derecho Integral"
    header.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = t.add_run(titulo.upper())
    run.bold = True
    for linea in contenido.split('\n'):
        doc.add_paragraph(linea)
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# 3. MENÚ LATERAL
with st.sidebar:
    st.title("⚖️ P&JIA Panel")
    opcion = st.radio("Módulos:", [
        "Analista de Expedientes (PDF)", 
        "Agenda de Plazos Procesales",
        "Calculadora de Beneficios", 
        "Generador de Escritos"
    ])
    st.markdown("---")
    st.caption("Especialidad: Civil, Penal y Laboral.")

# 4. MÓDULO: AGENDA DE PLAZOS
if opcion == "Agenda de Plazos Procesales":
    st.title("📅 Calculadora de Plazos Procesales")
    st.info("Calcula el vencimiento de recursos según el NCPP, CPC y NLPT.")
    
    col1, col2 = st.columns(2)
    with col1:
        f_notif = st.date_input("Fecha de Notificación:", datetime.now())
        materia = st.selectbox("Materia:", ["Penal", "Civil", "Laboral"])
    with col2:
        tipo = st.selectbox("Recurso/Acto:", [
            "Apelación de Auto (3 días)", "Apelación de Sentencia (5 días)", 
            "Casación (10 días)", "Contestación (Sumarísima - 5 días)", "Contestación (Abreviada - 10 días)"
        ])

    dias = 3 if "3 días" in tipo else 5 if "5 días" in tipo else 10
    vencimiento = f_notif + timedelta(days=dias)
    st.subheader(f"📌 Vencimiento Estimado: {vencimiento.strftime('%d/%m/%Y')}")
    st.warning("Nota: Verifique feriados judiciales antes de presentar.")

# 5. MÓDULO: ANALISTA EXPERTO (PDF)
elif opcion == "Analista de Expedientes (PDF)":
    st.title("📂 Analista Legal Multidisciplinario")
    archivo = st.file_uploader("Subir Expediente", type=["pdf"])
    if prompt := st.chat_input("¿Qué deseas analizar del expediente?"):
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            texto_pdf = extraer_texto_pdf(archivo) if archivo else ""
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "Eres P&JIA Core Pro. Experto en Penal (NCPP), Civil (Art. 140 CC) y Laboral (DL 728). Analiza el texto del PDF adjunto con rigor legal."},
                    {"role": "user", "content": f"PDF:\n{texto_pdf[:30000]}\n\nPREGUNTA:\n{prompt}"}
                ], "temperature": 0.1
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
            st.markdown(res["choices"][0]["message"]["content"])

# 6. CALCULADORA LABORAL
elif opcion == "Calculadora de Beneficios":
    st.title("🧮 Calculadora Laboral (Sector Privado)")
    sueldo = st.number_input("Sueldo Mensual", min_value=1025.0)
    meses = st.slider("Meses laborados", 1, 12, 6)
    af = st.checkbox("Asignación Familiar")
    base = sueldo + (102.50 if af else 0.0)
    st.metric("Estimado Total", f"S/. {(((base/6)*meses)*1.09) + (((base+(base/6))/12)*meses) + ((base/12)*meses):,.2f}")

# 7. GENERADOR DE ESCRITOS
elif opcion == "Generador de Escritos":
    st.title("📝 Redacción Jurídica Profesional")
    tipo_e = st.selectbox("Tipo:", ["Contestación", "Demanda", "Carta Notarial"])
    h = st.text_area("Hechos:")
    if st.button("Generar"):
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Experto redactor peruano. Usa Art. 140 CC para actos jurídicos. Estructura: Sumilla, Petitorio, Hechos, Derecho."},
                {"role": "user", "content": f"Genera {tipo_e} de: {h}"}
            ], "temperature": 0.2
        }
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
        st.session_state.escrito = res["choices"][0]["message"]["content"]
        st.markdown(st.session_state.escrito)
    if "escrito" in st.session_state:
        st.download_button("📥 Descargar Word", crear_word_profesional("Escrito", st.session_state.escrito), "PJIA_Escrito.docx")
