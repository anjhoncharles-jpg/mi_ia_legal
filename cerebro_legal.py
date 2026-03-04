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

# 4. MÓDULO: ASISTENTE JURÍDICO
if opcion == "Asistente Jurídico":
    st.title("⚖️ Asistente Jurídico Inteligente")
    st.info("Resúmenes analíticos: D.L. 728, Código Civil y Penal.")
    
    if prompt := st.chat_input("Consulta la normativa..."):
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "Eres P&JIA Core. No copies artículos textualmente. Ofrece resúmenes analíticos de la norma peruana. Estructura: 1. Resumen de la falta, 2. Implicancia legal, 3. Recomendación."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                }
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                res_data = response.json()
                if "choices" in res_data:
                    st.markdown(res_data["choices"][0]["message"]["content"])
                else:
                    st.error(f"Error de API: {res_data.get('error', {}).get('message', 'Clave no válida')}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# 5. MÓDULO: CALCULADORA DE BENEFICIOS (Optimizado)
elif opcion == "Calculadora de Beneficios":
    st.title("🧮 Calculadora de Beneficios Sociales (Régimen General)")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            sueldo = st.number_input("Sueldo Mensual (S/.)", min_value=1025.0, step=100.0)
            meses = st.slider("Meses laborados (en el semestre/año)", 1, 12, 6)
        with col2:
            asig_fam = st.checkbox("¿Tiene Asignación Familiar?")
            monto_af = 102.50 if asig_fam else 0.0
            st.write(f"Asignación Familiar: S/. {monto_af}")

    base = sueldo + monto_af
    
    st.markdown("---")
    st.subheader("📊 Estimación de Beneficios")
    
    res1, res2, res3 = st.columns(3)
    
    # Gratificación (Sueldo + AF)
    grati = (base / 6) * meses
    boni = grati * 0.09
    res1.metric("Gratificación + Bonif. (9%)", f"S/. {grati + boni:,.2f}")
    
    # CTS (Base + 1/6 Grati)
    cts = ((base + (base/6)) / 12) * meses
    res2.metric("CTS Proyectada", f"S/. {cts:,.2f}")
    
    # Vacaciones (Base / 12 meses)
    vacas = (base / 12) * meses
    res3.metric("Vacaciones Truncas", f"S/. {vacas:,.2f}")

    st.caption("Nota: Cálculos referenciales para el sector privado (Régimen General).")
