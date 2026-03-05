import streamlit as st
import requests
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import PyPDF2

# 1. ACCESO PRIVADO
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

# 2. CONFIGURACIÓN DE SISTEMA
st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")
raw_key = st.secrets.get("GROQ_API_KEY", "")
api_key = raw_key.replace("\n", "").replace("\r", "").replace(" ", "").replace('"', '').replace("'", "").strip()

# Función mejorada para extraer texto de PDF (más robusta)
def extraer_texto_pdf(archivo):
    try:
        lector = PyPDF2.PdfReader(archivo)
        texto = ""
        # Limitamos a las primeras 15 páginas para evitar saturar la memoria de la IA
        for i in range(len(lector.pages[:15])):
            texto += lector.pages[i].extract_text() + "\n"
        return texto
    except Exception as e:
        return f"Error al leer PDF: {e}"

# Función para Word Profesional
def crear_word_profesional(titulo_escrito, contenido):
    doc = Document()
    header = doc.sections[0].header
    p = header.paragraphs[0]
    p.text = "P&JIA - CONSULTORES LEGALES\nExpertos en Derecho Integral (Laboral, Civil, Penal)"
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
    st.subheader("Experto Legal Integral")
    opcion = st.radio("Módulos:", ["Asistente Jurídico (PDF)", "Calculadora de Beneficios", "Generador de Escritos"])
    st.markdown("---")
    st.info("Especialidad: Civil, Penal y Laboral.")

# 4. MÓDULO: ASISTENTE JURÍDICO INTEGRAL
if opcion == "Asistente Jurídico (PDF)":
    st.title("⚖️ Consultor Legal Multidisciplinario")
    st.write("Analiza expedientes, notificaciones o realiza consultas legales generales.")
    
    archivo_subido = st.file_uploader("Cargar documento para análisis (PDF)", type=["pdf"])
    
    if prompt := st.chat_input("Realiza tu consulta o pide analizar el PDF..."):
        texto_contexto = ""
        if archivo_subido:
            with st.spinner("Leyendo documento..."):
                texto_contexto = extraer_texto_pdf(archivo_subido)

        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                # Prompt del sistema como experto total
                sys_prompt = """Eres P&JIA Core, un eminente jurista peruano experto en:
                1. DERECHO PENAL: Código Penal y NCPP. Análisis de imputaciones fiscales y tipicidad.
                2. DERECHO LABORAL: D.L. 728, Ley 29497 y regímenes especiales.
                3. DERECHO CIVIL: Código Civil (Art. 140 para actos jurídicos, etc.) y Procesal Civil.
                
                Si se te entrega un PDF, ANALÍZALO DIRECTAMENTE. No des respuestas generales. 
                Sé crítico, detecta errores en plazos, falta de motivación o errores en la base legal de la contraparte/fiscalía."""
                
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": f"DOCUMENTO CARGADO:\n{texto_contexto[:12000]}\n\nCONSULTA:\n{prompt}"}
                    ], "temperature": 0.1
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
                st.markdown(res["choices"][0]["message"]["content"])
            except: st.error("Error de comunicación con el motor legal.")

# 5. MÓDULO: CALCULADORA (Igual)
elif opcion == "Calculadora de Beneficios":
    st.title("🧮 Calculadora de Beneficios (Régimen General)")
    sueldo = st.number_input("Sueldo Mensual (S/.)", min_value=1025.0)
    meses = st.slider("Meses laborados", 1, 12, 6)
    asig_fam = st.checkbox("¿Asignación Familiar?")
    base = sueldo + (102.50 if asig_fam else 0.0)
    st.metric("Gratificación + Bonif. (9%)", f"S/. {((base/6)*meses)*1.09:,.2f}")
    st.metric("CTS Proyectada", f"S/. {((base + (base/6))/12)*meses:,.2f}")

# 6. MÓDULO: GENERADOR DE ESCRITOS
elif opcion == "Generador de Escritos":
    st.title("📝 Generador de Escritos Legales")
    tipo_escrito = st.selectbox("Documento:", ["Denuncia/Contestación Penal", "Carta Notarial", "Contestación de Despido", "Demanda Laboral"])
    detalles = st.text_area("Detalle los hechos:")
    if st.button("Generar"):
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Redactor jurídico experto. Estructura formal peruana. Rigor legal absoluto."},
                {"role": "user", "content": f"Genera un(a) {tipo_escrito} basado en: {detalles}"}
            ], "temperature": 0.2
        }
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
        escrito = res["choices"][0]["message"]["content"]
        st.session_state.escrito_actual = escrito
        st.markdown(escrito)
        
    if "escrito_actual" in st.session_state:
        file_word = crear_word_profesional("Escrito Legal", st.session_state.escrito_actual)
        st.download_button("📥 Descargar Escrito (.docx)", file_word, "Escrito_PJIA.docx")
