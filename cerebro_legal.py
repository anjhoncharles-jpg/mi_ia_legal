import streamlit as st
import requests

# 1. ACCESO (Tus 5 usuarios)
USUARIOS = {"admin": "clave777", "user1": "peru2026", "user2": "legal20", "user3": "pjia01", "user4": "estudio5"}

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso P&JIA Core")
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

# 3. MENÚ LATERAL
with st.sidebar:
    st.title("⚖️ P&JIA Panel")
    opcion = st.radio("Seleccione función:", ["Asistente Jurídico", "Calculadora de Beneficios"])
    st.markdown("---")
    st.caption("Especialista Legal Perú 2026")

# 4. MÓDULO: ASISTENTE JURÍDICO (Resúmenes Analíticos)
if opcion == "Asistente Jurídico":
    st.title("⚖️ Asistente Jurídico Inteligente")
    st.info("Resúmenes ejecutivos basados en D.L. 728, Código Civil y Penal.")
    
    if prompt := st.chat_input("Consulta la normativa..."):
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.3-70b-8192",
                    "messages": [
                        {"role": "system", "content": "Eres P&JIA Core. No copies los artículos textualmente. Ofrece resúmenes analíticos y precisos de la norma peruana. Estructura: 1. Resumen de la falta/norma, 2. Implicancia legal, 3. Recomendación."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                }
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload).json()
                st.markdown(res["choices"][0]["message"]["content"])
            except:
                st.error("Error de conexión con la IA.")

# 5. MÓDULO: CALCULADORA DE BENEFICIOS (Nuevo)
elif opcion == "Calculadora de Beneficios":
    st.title("🧮 Calculadora de Beneficios Sociales (Régimen General)")
    
    col1, col2 = st.columns(2)
    with col1:
        sueldo = st.number_input("Sueldo Mensual (S/.)", min_value=0.0, value=1025.0)
        meses = st.number_input("Meses laborados en el periodo", min_value=1, max_value=12, value=6)
    
    with col2:
        asignacion = st.checkbox("¿Recibe Asignación Familiar?")
        monto_af = 102.50 if asignacion else 0.0
        st.write(f"Asignación Familiar: S/. {monto_af}")

    base_calculo = sueldo + monto_af
    
    st.markdown("### 📊 Resultados Estimados")
    c1, c2, c3 = st.columns(3)
    
    # Cálculos rápidos
    gratificacion = (base_calculo / 6) * meses
    bonificacion = gratificacion * 0.09
    cts_estimada = ((base_calculo + (sueldo/6)) / 12) * meses
    vacaciones = (base_calculo / 12) * meses

    c1.metric("Gratificación + Bonif.", f"S/. {gratificacion + bonificacion:,.2 False}")
    c2.metric("CTS Proyectada", f"S/. {cts_estimada:,.2f}")
    c3.metric("Vacaciones Truncas", f"S/. {vacaciones:,.2f}")
    
    st.warning("Nota: Estos montos son referenciales para el Régimen General. No incluyen descuentos de ley (AFP/ONP).")
