import requests
import subprocess
import os
from docx import Document
from datetime import datetime


# ============================================
#  CONFIGURACIÓN
# ============================================

RUTA_GUARDADO = "/mnt/c/aa_aa_postulacion/lettres_motivation"

# Tu token de acceso a Hugging Face:
HUGGING_FACE_TOKEN = "___________"

# Endpoint de la Inference API en Hugging Face:
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

# Headers para la solicitud HTTP
HEADERS = {
    "Authorization": f"Bearer {HUGGING_FACE_TOKEN}",
    "Content-Type": "application/json"
}



# Plantillas para francés e inglés
TEMPLATE_FR = """
Ray L. Vera
92200 Neuilly-sur-Seine
vera.ray.leonardo@gmail.com
+33 06-18-44-82-23

                                                                         Neuilly-sur-Seine, le {fecha}
                                                                         {empresa}
                                                                         {direccion_empresa}

Objet : Candidature au poste de {puesto_completo}

Madame, Monsieur,

{contenido_generado}

Dans l’attente de votre retour, je vous prie d’agréer, Madame, Monsieur, l’expression de mes salutations distinguées.

Ray L. VERA
"""

TEMPLATE_EN = """
Ray L. Vera
92200 Neuilly-sur-Seine
vera.ray.leonardo@gmail.com
+33 06-18-44-82-23

                                                                         Neuilly-sur-Seine, {fecha}
                                                                         {empresa}
                                                                         {direccion_empresa}

Subject: Application for the position of {puesto_completo}

Dear Sir or Madam,

{contenido_generado}

I look forward to hearing from you. 
Best regards,

Ray L. VERA
"""

# ============================================
#  FUNCIÓN PARA LEER Y PARSEAR prompt.txt
# ============================================

def leer_prompt_y_extraer_datos(ruta_archivo: str):
    """
    Lee el archivo prompt.txt y extrae:
      - Language
      - Company
      - Address
      - Job Title
    El resto del contenido se considera descripción del puesto (puesto_info).
    Devuelve un diccionario con la información.
    """
    datos = {
        "language": "FRENCH",  # Por defecto francés
        "company": "",
        "address": "",
        "job_title": "",
        "puesto_info": ""
    }

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    # Limpieza de líneas en blanco
    lineas = [l.strip() for l in lineas if l.strip()]

    contenido_puesto = []
    for linea in lineas:
        if linea.lower().startswith("language:"):
            datos["language"] = linea.split(":", 1)[1].strip().upper()
        elif linea.lower().startswith("company:"):
            datos["company"] = linea.split(":", 1)[1].strip()
        elif linea.lower().startswith("address:"):
            datos["address"] = linea.split(":", 1)[1].strip()
        elif linea.lower().startswith("job title:"):
            datos["job_title"] = linea.split(":", 1)[1].strip()
        else:
            contenido_puesto.append(linea)

    datos["puesto_info"] = "\n".join(contenido_puesto)
    return datos

# ============================================
#  FUNCIÓN PARA FORMAR LA PLANTILLA SEGÚN IDIOMA
# ============================================

def get_plantilla(language: str):
    """
    Retorna la plantilla correspondiente a Francés o Inglés.
    Soporta 'FRENCH' o 'ENGLISH' (ignora mayúsculas/minúsculas).
    Por defecto, francés.
    """
    if language == "ENGLISH":
        return TEMPLATE_EN
    else:
        return TEMPLATE_FR  # Por defecto francés

# ============================================
#  FUNCIÓN PARA LLAMAR A LA API DE HF
# ============================================

def llamar_api_huggingface(prompt, max_new_tokens=500, temperature=0.4):
    """
    Llama a la Inference API de Hugging Face vía requests.
    Retorna el texto generado.
    """
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature
        }
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()  # dispara excepción si status != 2xx

    # La respuesta suele ser una lista con dicts donde "generated_text" está la cadena generada
    data = response.json()
    # Ej: [{"generated_text": "..."}]

    # Extraemos el campo "generated_text"
    texto_generado = data[0]["generated_text"]

    return texto_generado

# ============================================
#  FUNCIÓN PRINCIPAL
# ============================================

def main():
    # 1) Leer y parsear prompt.txt
    datos_prompt = leer_prompt_y_extraer_datos("prompt.txt")
    language = datos_prompt["language"]
    nombre_empresa = datos_prompt["company"]
    direccion_empresa = datos_prompt["address"]
    puesto_completo = datos_prompt["job_title"] or "Poste Inconnu"  # fallback
    puesto_info = datos_prompt["puesto_info"]

    # 2) Configurar la plantilla en el idioma correcto
    plantilla = get_plantilla(language)

    # 3) Armar el prompt de texto que enviaremos a la IA
    if language == "ENGLISH":
        # Prompt en inglés
        prompt = f"""
You are Ray Leonardo VERA, Data Science graduate, 2 years of experience in data analysis.
Please write a cover letter in English, with a natural and enthusiastic tone, specifically tailored to this job:

Job details:
{puesto_info}

Important instructions:
- If the position requires more than 3 years of experience, mention you understand this requirement but are motivated to learn quickly.
- If there's a specific skill (e.g., SAS) not in your CV, state you have basic knowledge and learn fast.
- Be concise (~300 words), clear, natural, and professional.
- Write only the main body (no greeting or closing).
"""
    else:
        # Prompt en francés
        prompt = f"""
Tu es Ray Leonardo VERA, diplômé en Data Science, profil analyste avec 2 ans d'expérience.
Rédige une lettre de motivation en français, de façon naturelle et enthousiaste, adaptée précisément à ce poste:

Détails du poste:
{puesto_info}

Instructions importantes:
- Si le poste exige plus de 3 ans d'expérience, indique que tu comprends cette exigence mais es motivé à compenser par ta capacité d'apprentissage rapide.
- Si on demande une compétence spécifique (par exemple SAS) non listée dans ton CV, précise brièvement que tu connais les bases et apprends vite.
- Sois concis (environ 300 mots), clair, naturel, et professionnel.
- Écris uniquement le corps principal (sans les salutations initiales et finales).
"""

    # 4) Llamar a la API de Hugging Face para generar el texto
    print("⏳ Conectándose a la Inference API de Hugging Face...")
    resultado_completo = llamar_api_huggingface(prompt, max_new_tokens=500, temperature=0.7)

    # Para aislar el texto generado y remover el prompt duplicado
    contenido_generado = resultado_completo.split(prompt)[-1].strip()

    # 5) Armar la carta final
    fecha_actual = datetime.now().strftime("%d %B %Y")
    carta_final = plantilla.format(
        fecha=fecha_actual,
        empresa=nombre_empresa,
        direccion_empresa=direccion_empresa,
        puesto_completo=puesto_completo,
        contenido_generado=contenido_generado
    )

    # 6) Mostrar "preview" en pantalla
    print("\n==================== PRÉVISUALISATION / PREVIEW ====================")
    print(carta_final)
    print("====================================================================\n")

    # Preguntar si se quiere continuar con la conversión a PDF
    respuesta = input("¿Deseas convertir este documento a PDF con LibreOffice? (sí/no): ").strip().lower()
    if respuesta not in ("si", "sí"):
        print("Operación cancelada. No se generará el PDF.")
        return

    # 7) Si responde que sí, guardar DOCX y convertir a PDF
    os.makedirs(RUTA_GUARDADO, exist_ok=True)

    def abreviar(texto):
        palabras = texto.split()
        return ''.join([palabra[0].lower() for palabra in palabras[:5]])  # Máx 5 letras iniciales

    nombre_docx = f"lettre_{abreviar(puesto_completo)}_{abreviar(nombre_empresa)}.docx"
    ruta_docx = os.path.join(RUTA_GUARDADO, nombre_docx)

    # Guardar en .docx
    doc = Document()
    doc.add_paragraph(carta_final)
    doc.save(ruta_docx)

    # Convertir a PDF con LibreOffice
    try:
        subprocess.run([
            "libreoffice", "--headless", "--convert-to", "pdf", ruta_docx,
            "--outdir", RUTA_GUARDADO
        ], check=True)
        print(f"✅ Lettre créée et convertie en PDF avec succès à : {RUTA_GUARDADO}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al convertir a PDF: {e}")

# ============================================
#  EJECUCIÓN
# ============================================
if __name__ == "__main__":
    main()
