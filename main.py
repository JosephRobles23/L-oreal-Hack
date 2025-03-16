from fastapi import FastAPI, Request, Form, File, UploadFile
from twilio.rest import Client
import google.generativeai as genai
from dotenv import load_dotenv
import os

app = FastAPI()  # Se crea una instancia de FastAPI para definir y manejar rutas de la API.

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de Twilio
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Configurar la API de Gemini
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Nombre del asistente de skincare
derma_bot_name = "DermaBot AI"

# Webhook para Recibir Mensajes de WhatsApp
@app.post("/webhook")
async def whatsapp_webhook(request: Request, Body: str = Form(...), From: str = Form(...)):
    print(f"Mensaje recibido: {Body} de {From}")  # Depuración

    if "hola" in Body.lower() or "buenos días" in Body.lower():
        response_text = f"¡Hola! Soy {derma_bot_name}, tu asistente dermatológico de Skin Care. Para ayudarte, por favor envíame una foto de tu rostro para analizar tu piel. 📸"
    else:
        response_text = generate_llm_response(Body)
    
    send_whatsapp_message(From, response_text)
    return {"status": "ok"}

# Endpoint para Cargar Imágenes
@app.post("/upload")
async def upload_image(file: UploadFile = File(...), From: str = Form(...)):
    skin_conditions = analyze_skin(file)  # Simulación de análisis de imagen (esto puede mejorarse con un modelo real de visión por computadora)
    recommendations = recommend_products(skin_conditions)
    
    response_text = f"Análisis de piel completado. Detecté: {', '.join(skin_conditions)}. Aquí tienes algunas recomendaciones de L'Oréal:\n{recommendations}"
    send_whatsapp_message(From, response_text)
    return {"status": "ok"}


# Análisis de la Piel (Simulado)
def analyze_skin(file):
    # Simulación de análisis de piel con una IA de visión
    return ["Acné leve", "Piel seca"]  # Esto debe reemplazarse con detección real

# Simulación de recomendación de productos basados en las condiciones detectadas
def recommend_products(skin_conditions):
    recommendations = {
        "Acné leve": "Gel limpiador L'Oréal Pure-Clay para piel grasa y propensa al acné.",
        "Piel seca": "Crema hidratante L'Oréal Hydra Genius con ácido hialurónico."
    }
    return '\n'.join([recommendations[cond] for cond in skin_conditions if cond in recommendations])

def generate_llm_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error en la generación de respuesta: {str(e)}")
        return "Hubo un error al procesar tu mensaje. Inténtalo de nuevo."

# Nueva función para dividir el mensaje en partes de 1600 caracteres
def split_message(message, max_length=1600):
    return [message[i:i + max_length] for i in range(0, len(message), max_length)]

# Modificación en send_whatsapp_message para enviar mensajes largos en partes
def send_whatsapp_message(to, message):
    try:
        partes = split_message(message)  # Divide el mensaje si es muy largo
        for parte in partes:
            msg = client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                body=parte,
                to=to
            )
            print(f"Mensaje enviado con SID: {msg.sid}")
    except Exception as e:
        print(f"Error al enviar mensaje: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
