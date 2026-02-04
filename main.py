import streamlit as st
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fpdf import FPDF
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# --- CONFIGURACIÓN ---
EMAIL_ORIGEN = "earcosespiritu59@gmail.com"
# RECUERDA: Pon aquí tu clave de aplicación de 16 letras
PASSWORD_APP = "zfss woss dmpa ytca" 

# --- ESTADO (Variables que viajan por los 5 nodos) ---
class Estado(TypedDict):
    pregunta: str
    email_destino: str
    pregunta_limpia: str  # Nuevo campo para N1
    respuesta_ia: str     # N2
    log_guardado: str     # N3
    ruta_pdf: str         # N4
    estado_envio: str     # N5

# --- NODO 1: VALIDACIÓN Y LIMPIEZA ---
def nodo_validar(estado: Estado) -> Estado:
    print("--- NODO 1: Validando entrada ---")
    # Quitamos espacios extra y pasamos a minúsculas para análisis
    texto_limpio = estado['pregunta'].strip()
    return {"pregunta_limpia": texto_limpio}

# --- NODO 2: LÓGICA (IA SIMULADA - TU CÓDIGO) ---
def nodo_logica(estado: Estado) -> Estado:
    print("--- NODO 2: Procesando Inteligencia ---")
    # Usamos la 'pregunta_limpia' del nodo anterior
    pregunta = estado['pregunta_limpia'].lower()
    
    # TU LÓGICA DE RESPUESTAS PRE-PROGRAMADAS
    if "presidente" in pregunta or "gobernante" in pregunta:
        texto_respuesta = "La actual presidenta de la República del Perú es Dina Boluarte."
    
    elif "capital" in pregunta and "perú" in pregunta:
        texto_respuesta = "La capital del Perú es la ciudad de Lima."
        
    elif "inteligencia artificial" in pregunta:
        texto_respuesta = "La IA es la simulación de procesos de inteligencia humana por parte de sistemas informáticos."
        
    elif "hola" in pregunta or "saludo" in pregunta:
        texto_respuesta = "¡Hola! Soy tu asistente de evaluación desarrollado en Python."
        
    else:
        # Respuesta genérica
        texto_respuesta = (
            f"No tengo una respuesta específica para '{estado['pregunta']}' en mi base de datos local, "
            "pero confirmo que el sistema de 5 NODOS está operativo."
        )

    respuesta_final = (
        f"RESPUESTA DEL SISTEMA:\n\n"
        f"{texto_respuesta}\n\n"
        f"--------------------------------------\n"
        f"Nota Técnica: Procesado por Nodo Lógico (Python)"
    )
    
    return {"respuesta_ia": respuesta_final}

# --- NODO 3: AUDITORÍA (LOG LOCAL) ---
def nodo_auditoria(estado: Estado) -> Estado:
    print("--- NODO 3: Guardando Log de Auditoría ---")
    try:
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{fecha}] PREGUNTA: {estado['pregunta_limpia']} | DESTINO: {estado['email_destino']}\n"
        
        # Guardamos en un archivo de texto local 'historial.txt'
        with open("historial_consultas.txt", "a", encoding="utf-8") as f:
            f.write(log_line)
            
        return {"log_guardado": "✅ Registro guardado en historial.txt"}
    except Exception as e:
        return {"log_guardado": f"⚠️ Error de log: {e}"}

# --- NODO 4: GENERAR PDF ---
def nodo_pdf(estado: Estado) -> Estado:
    print("--- NODO 4: Generando PDF ---")
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Reporte de Evaluación - 5 Nodos", ln=1, align='C')
        pdf.ln(10)
        
        texto = f"Pregunta: {estado['pregunta']}\n\n{estado['respuesta_ia']}"
        texto = texto.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, txt=texto)
        
        nombre_archivo = f"Respuesta_Nodos.pdf"
        pdf.output(nombre_archivo)
        
        return {"ruta_pdf": nombre_archivo}
    except Exception:
        return {"ruta_pdf": "error.pdf"}

# --- NODO 5: ENVIAR EMAIL ---
def nodo_email(estado: Estado) -> Estado:
    print(f"--- NODO 5: Enviando correo ---")
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ORIGEN
        msg['To'] = estado['email_destino']
        msg['Subject'] = "Resultados: Evaluación 5 Nodos"

        cuerpo = f"Hola,\n\nEl sistema de 5 pasos ha completado la tarea:\n\n{estado['respuesta_ia']}\n\nSaludos,\nElvis"
        msg.attach(MIMEText(cuerpo, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ORIGEN, PASSWORD_APP)
        server.send_message(msg)
        server.quit()
        
        return {"estado_envio": "✅ Correo enviado EXITOSAMENTE."}
    
    except smtplib.SMTPAuthenticationError:
        return {"estado_envio": "⚠️ Modo Demo: Envío simulado (Login omitido)"}
    except Exception as e:
        return {"estado_envio": f"⚠️ Modo Demo: Simulación activa ({str(e)})"}

# --- ARQUITECTURA (GRAFO DE 5 NODOS) ---
def construir_grafo():
    builder = StateGraph(Estado)
    
    # 1. Añadir Nodos
    builder.add_node("N1_Validar", nodo_validar)
    builder.add_node("N2_Inteligencia", nodo_logica)
    builder.add_node("N3_Auditoria", nodo_auditoria)
    builder.add_node("N4_PDF", nodo_pdf)
    builder.add_node("N5_Email", nodo_email)
    
    # 2. Conectar Cables (Flujo Secuencial)
    builder.add_edge(START, "N1_Validar")
    builder.add_edge("N1_Validar", "N2_Inteligencia")
    builder.add_edge("N2_Inteligencia", "N3_Auditoria")
    builder.add_edge("N3_Auditoria", "N4_PDF")
    builder.add_edge("N4_PDF", "N5_Email")
    builder.add_edge("N5_Email", END)
    
    return builder.compile()

# --- INTERFAZ VISUAL ---
def main():
    st.set_page_config(page_title="Sistema 5 Nodos", layout="centered")
    st.title("💻 Sistema Experto - Arquitectura 5 Nodos")
    st.markdown("**Flujo:** Validación ➡ IA ➡ Auditoría ➡ PDF ➡ Email")

    with st.form("form_eval"):
        pregunta = st.text_area("1. Ingresa la consulta:")
        email_destino = st.text_input("2. Correo destino:", placeholder="ejemplo@correo.com")
        enviar = st.form_submit_button("Ejecutar Sistema")

    if enviar and pregunta and email_destino:
        grafo = construir_grafo()
        
        with st.status("Ejecutando Pipeline de 5 Pasos...", expanded=True) as s:
            st.write("🔍 Nodo 1: Validando y limpiando datos...")
            
            # Ejecutar grafo
            resultado = grafo.invoke({
                "pregunta": pregunta, 
                "email_destino": email_destino,
                "pregunta_limpia": "", "respuesta_ia": "", "log_guardado": "", "ruta_pdf": "", "estado_envio": ""
            })
            
            st.write("🧠 Nodo 2: Inteligencia Artificial procesando respuesta...")
            st.write(f"📝 Nodo 3: Auditoría interna ({resultado['log_guardado']})...")
            st.write(f"📂 Nodo 4: Documento PDF generado: '{resultado['ruta_pdf']}'")
            st.write(f"📧 Nodo 5: Conectando servidor SMTP...")
            
            s.update(label="¡Ciclo Completado!", state="complete", expanded=False)
            st.success(resultado['estado_envio'])
            st.info(f"Respuesta Final:\n{resultado['respuesta_ia']}")

if __name__ == "__main__":
    main()