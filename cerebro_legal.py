import streamlit as st
import os
import requests
from docx import Document
from io import BytesIO
import PyPDF2

# 1. CONFIGURACIÓN DE USUARIOS
USUARIOS_PERMITIDOS = {
    "admin": "clave777",
    "user1": "peru2026",
    "user2": "legal20",
    "user3": "pjia01",
    "user4": "estudio5"
}

# 2. FUNCIÓN DE LOGIN
def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.set_page_config(page_title="Login P&JIA", page_icon="🔐")
        st.title("🔐 Acceso Privado P&JIA")
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar"):
            if user in USUARIOS_PERMITIDOS and USUARIOS_PERMITIDOS[user] == password:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        return False
    return True

if not login():
    st.stop()

# --- CONFIGURACIÓN DE LA IA ---
API_KEY = st.secrets["GROQ_API_KEY"]

st.set_page_config(page_title="P&JIA Core Pro", page_icon="⚖️", layout="wide")

# PANEL LATERAL (HERRAMIENTAS)
with st.sidebar:
    st.title("🛠️ Panel de Control")
    st.markdown("---")
    
    opcion = st.selectbox("Selecciona una función:", 
                         ["Asistente Legal", "Calculadora Laboral", "Generador de Documentos"])
    
    st.markdown("---")
    archivo_subido = st.file_uploader("📁 Analizar PDF (Contratos/Demandas)", type=['pdf'])
    
    if st.button("🗑️ Limpiar Historial"):
        st.session_state.messages = []
        st.rerun()

# FUNCIÓN PARA EXTRAER TEXTO DE PDF
def extraer_pdf(archivo):
    lector = PyPDF2.PdfReader(archivo)
    texto = ""
    for pagina in lector.pages:
        texto += pagina.extract_text()
    return texto

# --- LÓGICA DE P&JIA CORE ---

if opcion == "Asistente Legal":
    st.title("⚖️ Asistente Jurídico Inteligente")
    st.info("Especializado en Derecho Laboral, Civil y Penal del Perú.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Consulta la ley o sube un PDF..."):
        contexto_adicional = ""
        if archivo_subido:
            with st.spinner("Leyendo PDF..."):
                texto_pdf = extraer_pdf(archivo_subido)
                contexto_adicional = f"\n\nCONTENIDO DEL DOCUMENTO SUBIDO:\n{texto_pdf}"
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analizando normativa peruana..."):
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json={
                        "model": "llama3-70b-8192",
                        "messages": [
                            {"role": "system", "content": "Eres P&JIA Core, experto en leyes peruanas. Prohibido inventar leyes. Cita D.L. 728, Código Civil y Código Penal exactamente. Estructura: Base Legal, Análisis, Conclusión."},
                            {"role": "user", "content": prompt + contexto_adicional}
                        ],
                        "temperature": 0.1
                    }
                )
                full_res = response.json()["choices"][0]["message"]["content"]
                st.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                
                # Botón Word
                doc = Document()
                doc.add_heading('P&JIA Core - Informe', 0)
                doc.add_paragraph(full_res)
                bio = BytesIO()
                doc.save(bio)
                st.download_button("📥 Descargar Informe", bio.getvalue(), "informe.docx")

elif opcion == "Calculadora Laboral":
    st.title("🧮 Calculadora de Beneficios (Perú)")
    col1, col2 = st.columns(2)
    with col1:
        sueldo = st.number_input("Sueldo Bruto (S/)", min_value=0.0, value=1025.0)
        meses = st.number_input("Meses trabajados", min_value=0, max_value=12, value=6)
    with col2:
        gratificacion = (sueldo / 6) * meses
        cts = (sueldo + (sueldo/6)) / 12 * meses
        st.metric("Estimado Gratificación", f"S/ {gratificacion:.2f}")
        st.metric("Estimado CTS", f"S/ {cts:.2f}")
    st.warning("Nota: Estos valores son referenciales. La IA puede ayudarte a detallar el cálculo en el chat.")

elif opcion == "Generador de Documentos":
    st.title("📝 Generador de Plantillas Jurídicas")
    tipo_doc = st.text_input("¿Qué documento necesitas? (Ej: Demanda de alimentos, Contrato de alquiler)")
    if st.button("Generar Plantilla Profesional"):
        with st.spinner("Redactando..."):
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": "llama3-70b-8192",
                    "messages": [{"role": "system", "content": "Genera plantillas legales formales para Perú."},
                                 {"role": "user", "content": f"Redacta una plantilla profesional de {tipo_doc}"}]
                }
            )
            plantilla = response.json()["choices"][0]["message"]["content"]
            st.text_area("Vista previa:", plantilla, height=400)
            doc = Document(); doc.add_paragraph(plantilla); bio = BytesIO(); doc.save(bio)
            st.download_button("📥 Descargar Plantilla", bio.getvalue(), "plantilla.docx")
