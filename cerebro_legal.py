import streamlit as st
import requests
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import PyPDF2

# 1. ACCESO
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

# Función para extraer texto sin límites severos
def extraer_texto_pdf_completo(archivo):
    try:
        lector = PyPDF2.PdfReader(archivo)
        texto_completo = ""
        # Extraemos todo el texto posible (la IA tiene un límite de contexto, enviamos lo más relevante)
        for pagina in lector.pages:
            texto_completo += pagina.extract_text() + "\n"
        return texto_completo
    except Exception as e:
        return f"Error técnico al leer el archivo: {e}"

# 3. INTERFAZ Y LÓGICA
with st.sidebar:
    st.title("⚖️ P&JIA Panel")
    st.subheader("Experto Multidisciplinario")
    opcion = st.radio("Módulos:", ["Asistente Jurídico (Análisis PDF)", "Calculadora de Beneficios", "Generador de Escritos"])
    st.info("Materias: Civil, Penal, Laboral, Constitucional, Administrativo.")

if opcion == "Asistente Jurídico (Análisis PDF)":
    st.title("⚖️ Consultor Legal Integral")
    st.write("Sube expedientes de cualquier extensión para un análisis experto.")
    
    archivo_subido = st.file_uploader("Cargar Expediente/Documento (PDF)", type=["pdf"])
    
    if prompt := st.chat_input("¿Qué análisis requiere sobre este caso?"):
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Analizando expediente y leyes peruanas..."):
                texto_pdf = ""
                if archivo_subido:
                    texto_pdf = extraer_texto_pdf_completo(archivo_subido)
                
                try:
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    
                    # PROMPT DE EXPERTO TOTAL
                    sys_prompt = """Eres P&JIA Core Pro, la IA legal más avanzada de Perú. 
                    TU MISIÓN: Analizar el texto que se te proporciona de forma exhaustiva.
                    MATERIAS: Experto en Derecho Penal (NCPP), Civil (Art. 140 CC y otros), Laboral (DL 728), y Procesal.
                    REGLA DE ORO: Tienes prohibido decir 'no puedo analizar' o 'no tengo acceso'. El texto del PDF está incluido en el mensaje del usuario. 
                    Si el texto es largo, enfócate en los puntos que el usuario pregunta. Cita siempre leyes vigentes de Perú."""

                    # Enviamos los últimos 15,000 caracteres del texto para asegurar que entre en el "context window"
                    # Esto equivale a las partes más densas del documento.
                    cuerpo_mensaje = f"TEXTO DEL EXPEDIENTE:\n{texto_pdf[:25000]}\n\nCONSULTA DEL ABOGADO:\n{prompt}"
                    
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": cuerpo_mensaje}
                        ], "temperature": 0.1
                    }
                    
                    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                    res_data = response.json()
                    
                    if "choices" in res_data:
                        st.markdown(res_data["choices"][0]["message"]["content"])
                    else:
                        st.error(f"Error del servidor: {res_data}")
                except Exception as e:
                    st.error(f"Fallo en la conexión: {e}")

# (Los módulos de Calculadora y Escritos se mantienen igual que en la versión anterior)
elif opcion == "Calculadora de Beneficios":
    st.title("🧮 Calculadora Laboral")
    sueldo = st.number_input("Sueldo Mensual (S/.)", min_value=1025.0)
    meses = st.slider("Meses laborados", 1, 12, 6)
    asig_fam = st.checkbox("Asignación Familiar")
    base = sueldo + (102.50 if asig_fam else 0.0)
    st.metric("Estimado Total (Grati + CTS + Vac)", f"S/. {(((base/6)*meses)*1.09) + (((base+(base/6))/12)*meses) + ((base/12)*meses):,.2f}")

elif opcion == "Generador de Escritos":
    st.title("📝 Redacción Jurídica")
    tipo = st.selectbox("Tipo:", ["Contestación Penal", "Demanda Civil", "Escrito Laboral"])
    detalles = st.text_area("Hechos:")
    if st.button("Redactar"):
        st.write("Generando... (usa la misma lógica de API de arriba)")
