# Generador automático de Lettre de Motivation adaptada usando Hugging Face (Online API)

# 1. Instalar primero las librerías necesarias:
# pip install python-docx requests

import requests
from docx import Document
from datetime import datetime
import subprocess
import os

# INFORMACIÓN DE CV (puedes modificar aquí fácilmente)
cv_info = """
Ray Leonardo VERA
92200 Neuilly-sur-Seine
vera.ray.leonardo@gmail.com

Expériences professionnelles :
- Data Scientist / Analyst en Alternance chez RLE - SNCF (sept. 2023 - sept. 2024)
  Modèles prédictifs, BigQuery, Power BI
- Freelancer Analyst chez Computer Parts Denmark ApS (janv. 2023 - août 2023)

Formations :
- Master Chef de Projet Informatique - Data Scientist (IA School Paris)
- Licence Génie Électrique (Université de Lille)

Compétences clés :
- Modélisation prédictive, Machine Learning, NLP
- Big Data : PySpark, Databricks, GCP, AWS
- SQL, NoSQL (MongoDB)
- Visualisation : Power BI, Tableau
- Python, SQL
- Français, Espagnol, Anglais (courant)
"""

# MODELO CARTA DE MOTIVACIÓN (modifica aquí tu modelo base si lo deseas)
lettre_modele = """
Ray L. VERA
92200 Neuilly-sur-Seine
vera.ray.leonardo@gmail.com
+33 06-18-44-82-23

{telefono:>70}
{fecha_empresa:>70}
{empresa:>70}
{direccion_empresa:>70}

Objet : Candidature au poste de {puesto_completo}

Madame, Monsieur,

{contenido_generado}

Dans l’attente de votre retour, je vous prie d’agréer, Madame, Monsieur, l’expression de mes salutations distinguées.

Ray L. VERA
"""

# Solicitar datos sobre el puesto
puesto_info = input("Pega aquí la descripción del puesto:\n")
nombre_empresa = input("Nombre exacto de la empresa: ")
direccion_empresa = input("Dirección de la empresa (ej: Paris, France): ")
nombre_puesto = puesto_info.split('\n')[0]

# Inicializar HuggingFace API (requiere token gratuito)
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": "Bearer TU_TOKEN_HUGGINGFACE"}  # <-- Aquí coloca tu token

# Prompt personalizado (modifícalo aquí para ajustes de estilo)
prompt = f"""
[INSTRUCTION] La lettre doit être impérativement rédigée en français uniquement.

Tu es Ray Leonardo VERA, diplômé en Data Science, avec l'expérience suivante :
{cv_info}

Adapte la lettre de motivation suivante au poste décrit ci-dessous, en personnalisant de manière claire, non robotique, et en ajoutant des commentaires pertinents sur ta motivation ou personnalité si nécessaire :

Lettre modèle:
{lettre_modele}

Description du poste visé :
{puesto_info}

Adapte spécifiquement :
- L'objet de la lettre doit être : "Candidature au poste de {nombre_puesto} chez {nombre_empresa}"
- Montre ta personnalité, ton intérêt spécifique pour l'entreprise, adapte précisément aux compétences demandées.
- Si le poste demande SAS (non mentionné dans ton CV), mentionne brièvement que tu connais les bases et apprends rapidement si pertinent.
- Reste formel, concis, clair.
- La lettre doit être impérativement rédigée en français uniquement.

Génère uniquement le corps de la lettre (sans les salutations de début et fin).
"""

# Generar carta personalizada
def generar_texto(prompt):
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt, "parameters": {"max_new_tokens": 500, "temperature": 0.7}})
    return response.json()[0]['generated_text']

texto_carta = generar_texto(prompt)

# Fecha actual formateada
fecha_actual = datetime.now().strftime("%d %B %Y")

# Carta final
contenido_carta = lettre_modele.format(
    telefono="+33 06-18-44-82-23",
    fecha=fecha_actual,
    fecha_actual=fecha_actual,
    empresa=nombre_empresa,
    direccion_empresa=input("Dirección empresa (ej: Paris, France): "),
    puesto_completo=nombre_puesto,
    contenido_generado=texto_carta
)

# Crear y guardar documento Word
ruta_guardado = r"/mnt/c/aa_aa_postulacion/lettres_motivation"

# Abreviar nombres largos para archivo
nombre_archivo = lambda texto: ''.join([palabra[0].lower() for palabra in texto.split()[:5]])

nombre_docx = f"lettre_{nombre_archivo(nombre_puesto)}_{nombre_archivo(nombre_empresa)}.docx"
doc = Document()
doc.add_paragraph(contenido_carta)
doc.save(os.path.join(ruta_guardado, nombre_archivo))

# Convertir directamente a PDF con libreoffice (WSL)
subprocess.run([
    "libreoffice", "--headless", "--convert-to", "pdf",
    os.path.join(ruta_guardado, nombre_archivo), "--outdir", ruta_guardado
], check=True)

print(f"Carta guardada exitosamente en DOCX y PDF en {ruta_guardado}")
