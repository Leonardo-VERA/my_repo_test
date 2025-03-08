# ==========================================
# Generador automático Lettre de Motivation
# Adaptado con Mistral (Hugging Face) en WSL
# ==========================================

# Instala antes estas dependencias:
# pip install python-docx transformers torch sentencepiece

import subprocess
import os
from docx import Document
from transformers import pipeline
from datetime import datetime

# ========= MODIFICA AQUÍ TU INFORMACIÓN ============
cv_info = """
Ray Leonardo VERA
92200 Neuilly-sur-Seine
vera.ray.leonardo@gmail.com

2 ans d'expérience en Analyse de Données, Big Data, automatisation.
Expertise : Tableau, Power BI, SQL & Python, ML, NLP, Big Data, GCP & AWS.
Langues : Français, Espagnol, Anglais.

Expériences :
- Data Scientist / Analyst chez RLE-SNCF (sept.2023-sept.2024)
- Freelancer Analyst chez Computer Parts Denmark (janv.-août 2023)

Formation :
- Master Chef Projet Informatique - Data Scientist (IA School Paris)
- Bootcamp Data Science, Artefact School of Data
"""

from docx import Document
from transformers import pipeline
from datetime import datetime
import subprocess
import os

# ========== Modifica aquí tu info base ==========
ruta_guardado = "/mnt/c/aa_aa_postulacion/lettres_motivation"

lettre_modele = """
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

# ================================================

# Inputs para personalización
puesto_info = input("👉 Pega aquí la descripción completa del puesto:\n\n")
nombre_empresa = input("👉 Nombre exacto empresa: ")
direccion_empresa = input("👉 Dirección empresa (opcional, Enter para omitir): ")
puesto_completo = puesto_info.split('\n')[0]

# Prompt personalizado (modifícalo aquí para ajustes de estilo)
prompt = f"""
La lettre doit être impérativement rédigée en français uniquement.
Tu es Ray Leonardo VERA, diplômé en Data Science, profil analyste avec 2 ans d'expérience. 

CV:
- Expertise en Data Visualisation (Power BI, Tableau), Python, SQL, Big Data, modélisation prédictive.
- Français, Espagnol, Anglais courant.
- Expérience: Alternance Data Scientist chez SNCF (Python, BigQuery), stage Analyste BI au Danemark.

Rédige une lettre de motivation courte, personnalisée (non robotique), avec enthousiasme et personnalité, adaptée précisément à ce poste:

{puesto_info}

Instructions importantes:
- Si le poste exige plus de 3 ans d'expérience, indique que tu comprends cette exigence mais es motivé à compenser par ta capacité d'apprentissage rapide.
- Si on demande une compétence spécifique (par exemple SAS) non listée dans ton CV, précise brièvement que tu connais les bases et apprends vite.
- Sois concis (environ 300 mots), clair, naturel, et professionnel.
- Écris uniquement le corps principal (sans les salutations initiales et finales).
"""

# Inicializar el modelo IA (Mistral)
print("⏳ Cargando modelo de IA (puede tomar ~1 min la primera vez)...")
generador = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.2", device="cpu")

# Generar texto con IA
resultado = generador(prompt, max_new_tokens=500, temperature=0.7)
contenido_generado = resultado[0]["generated_text"].split(prompt)[-1].strip()

# Fecha actual
fecha_actual = datetime.now().strftime("%d %B %Y")

# Información adicional del usuario
nombre_empresa = input("👉 Nombre exacto de la empresa: ")
direccion_empresa = input("👉 Dirección de la empresa (ej: Paris, France): ")
puesto_completo = puesto_info.split("\n")[0]

# Preparar carta final
carta_final = lettre_modele.format(
    fecha=fecha_actual,
    empresa=nombre_empresa,
    direccion_empresa=direccion_empresa,
    puesto_completo=puesto_completo,
    contenido_generado=contenido_generado
)

# Nombre abreviado automático del archivo
def abreviar(texto):
    palabras = texto.split()
    return ''.join([palabra[0].lower() for palabra in palabras[:5]])

fecha_actual = datetime.now().strftime("%d %B %Y")
nombre_docx = f"lettre_{abreviar(puesto_completo)}_{abreviar(nombre_empresa)}.docx"
ruta_docx = os.path.join(ruta_guardado, nombre_docx)

# Crear directorio si no existe
os.makedirs(ruta_guardado, exist_ok=True)

# Guardar archivo .docx
doc = Document()
doc.add_paragraph(carta_final)
doc.save(ruta_docx)

# Convertir directamente a PDF usando LibreOffice desde WSL
try:
    subprocess.run([
        "libreoffice", "--headless", "--convert-to", "pdf", ruta_docx,
        "--outdir", ruta_guardado
    ], check=True)

    print(f"✅ Lettre creada y convertida exitosamente a PDF en:\n{ruta_guardado}")

except subprocess.CalledProcessError as e:
    print(f"❌ Error al convertir a PDF: {e}")

# ======== Función para abreviar nombres largos ========
def abreviar(texto):
    palabras = texto.split()
    return ''.join([palabra[0].lower() for palabra in palabras[:5]])  # Máx 5 letras iniciales
