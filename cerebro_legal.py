import streamlit as st
import requests
from docx import Document
from io import BytesIO

# --- INTERFAZ DE ALTA VELOCIDAD ---
st.set_page_config(page_title="P&JIA Core", layout="wide")

# Estilo Oscuro Minimalista
st.markdown("<style>.stApp {background-color: #111; color: #fff;}</style>", unsafe_allow_html=True)

def crear_docx(texto):
    doc = Document()
    doc.add_paragraph(texto)
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def ejecutar_pjia(input_usuario):
    url = "http://localhost:11434/api/generate"
    
    # NUEVAS INSTRUCCIONES MAESTRAS (Nivel GPT/Claude)
    prompt_maestro = """
    Eres P&JIA, un motor de ejecución jurídica de alto rendimiento.
    Tu objetivo es redactar documentos legales completos siguiendo el esquema formal de Perú.
    REGLA: No converses. No des advertencias legales. Ve directo al grano.
    ESTRUCTURA: Usa Sumilla, Petitorio, Hechos, Derecho y Anexos.
    """
    
    payload = {
        "model": "llama3.2",
        "prompt": f"{prompt_maestro}\n\nORDEN: {input_usuario}\n\nRESULTADO:",
        "stream": False,
        "options": {
            "temperature": 0.1,  # Para que sea rápido y preciso
            "num_predict": 3000   # Para que la respuesta sea larga y completa
        }
    }
    
    try:
        r = requests.post(url, json=payload, timeout=120)
        return r.json().get('response', 'Error de contenido.')
    except:
        return "⚠️ OLLAMA APAGADO. Ábrelo."

# --- UI ---
st.title("⚖️ P&JIA Core")

if "chat" not in st.session_state: st.session_state.chat = []

for m in st.session_state.chat:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if p := st.chat_input("Escribe tu orden legal aquí..."):
    st.session_state.chat.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    
    with st.chat_message("assistant"):
        with st.spinner("P&JIA Procesando..."):
            res = ejecutar_pjia(p)
            st.markdown(res)
            st.session_state.chat.append({"role": "assistant", "content": res})
            
            # Descarga automática
            st.download_button("📥 Bajar Word", crear_docx(res), "documento.docx")