import streamlit as st
import requests
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# 1. ACCESO (Tus 5 usuarios)
USUARIOS = {"admin": "clave777", "user1": "peru2026", "user2": "legal20", "user3": "pjia01", "user4": "estudio5"}

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.set_page_config(page_title="Login P&JIA", page_icon="🔐")
    st.title("🔐 Acceso Privado P&JIA Core")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u in USUARIOS and USUARIOS[u] == p:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# 2. CONFIGURACIÓN Y LIMPIEZA DE API
st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")
raw_key = st.secrets.get("GROQ_API_KEY", "")
api_key = raw_key.replace("\n", "").replace("\r", "").replace(" ", "").replace('"', '').replace("'", "").strip()

# Función para el Word Profesional
def crear_word_profesional(titulo_escrito, contenido):
    doc = Document()
    header = doc.sections[0].header
    p = header.paragraphs[0]
    p.text = "P&JIA - CONSULTORES LEGALES\nEspecialistas en Derecho Laboral, Civil y Penal"
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = t.add_run(titulo_escrito.upper())
    run.bold = True
    run.font.size = Pt(14)
    
    doc.add_paragraph("-" * 30).alignment = WD_ALIGN_PARAGRAPH.CENTER

    for linea in contenido.split('\n'):
        para = doc.add_paragraph()
        if any(keyword in linea.upper() for keyword in ["SUMILLA:", "PETITORIO:", "FUNDAMENTOS:", "BASE LEGAL:"]):
            run = para.add_run(linea)
            run.bold = True
        else:
            para.add_run(linea)
            
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# 3. MENÚ LATERAL
with st.sidebar:
    st.title("⚖️ P&JIA Panel")
    opcion = st.radio("Seleccione función:", ["Asistente Jurídico", "Calculadora de Beneficios", "Generador de Escritos"])
    st.markdown("---")
    st.caption("Especialista Legal Perú 2026")

# 4. MÓDULO: ASISTENTE JURÍDICO
if opcion == "Asistente Jurídico":
    st.title("⚖️ Asistente Jurídico Inteligente")
    if prompt := st.chat_input("Consulta la normativa..."):
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "Eres P&JIA Core. Cita leyes reales. RECUERDA: El Acto Jurídico es el Art. 140 del Código Civil. No inventes artículos. Resúmenes analíticos: 1. Resumen, 2. Implicancia, 3. Recomendación."},
                        {"role": "user", "content": prompt}
                    ], "temperature": 0.1
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
                st.markdown(res["choices"][0]["message"]["content"])
            except: st.error("Error de conexión.")

# 5. MÓDULO: CALCULADORA DE BENEFICIOS
elif opcion == "Calculadora de Beneficios":
    st.title("🧮 Calculadora de Beneficios")
    col1, col2 = st.columns(2)
    with col1:
        sueldo = st.number_input("Sueldo Mensual (S/.)", min_value=1025.0)
        meses = st.slider("Meses laborados", 1, 12, 6)
    with col2:
        asig_fam = st.checkbox("¿Asignación Familiar?")
        base = sueldo + (102.50 if asig_fam else 0.0)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Gratificación + Bonif.", f"S/. {((base/6)*meses)*1.09:,.2f}")
    c2.metric("CTS Proyectada", f"S/. {((base + (base/6))/12)*meses:,.2f}")
    c3.metric("Vacaciones", f"S/. {(base/12)*meses:,.2f}")

# 6. MÓDULO: GENERADOR DE ESCRITOS
elif opcion == "Generador de Escritos":
    st.title("📝 Generador de Escritos Legales")
    tipo_escrito = st.selectbox("Tipo de documento:", ["Carta Notarial", "Contestación de Despido", "Demanda Laboral", "Recurso de Apelación"])
    detalles = st.text_area("Hechos clave:")
    
    if st.button("Generar Borrador"):
        if detalles:
            with st.spinner("Redactando conforme a ley..."):
                try:
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": "Eres un experto redactor jurídico peruano. RECUERDA: El Acto Jurídico es el Art. 140 del Código Civil. Cita D.L. 728 o Código Penal según corresponda. Usa SUMILLA, PETITORIO, HECHOS y DERECHO."},
                            {"role": "user", "content": f"Genera un(a) {tipo_escrito} basado en: {detalles}"}
                        ], "temperature": 0.2
                    }
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
                    escrito = res["choices"][0]["message"]["content"]
                    st.session_state.escrito_actual = escrito
                    st.session_state.tipo_actual = tipo_escrito
                    st.markdown("---")
                    st.subheader("📄 Borrador Generado")
                    st.markdown(escrito)
                except: st.error("Error al generar.")
        else: st.error("Faltan detalles.")

    if "escrito_actual" in st.session_state:
        file_word = crear_word_profesional(st.session_state.tipo_actual, st.session_state.escrito_actual)
        st.download_button("📥 Descargar Escrito P&JIA (.docx)", file_word, f"PJIA_{st.session_state.tipo_actual}.docx")
