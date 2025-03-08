# app.py
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import cv2
from tensorflow.keras.models import load_model
import os

# Cargar el modelo entrenado
model = load_model("mnist_model.h5")

st.title("Reconocimiento de Dígitos a Mano")
st.write("Dibuja un dígito en el canvas y el modelo lo reconocerá.")

# Crear el canvas para dibujar
canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0)",    # Fondo transparente en el dibujo
    stroke_width=10,
    stroke_color="#FFFFFF",           # Dibuja con color blanco
    background_color="#000000",       # Fondo negro para emular MNIST (fondo oscuro, dígito claro)
    height=280,
    width=280,
    drawing_mode="freedraw",
    key="canvas"
)

if canvas_result.image_data is not None:
    # Convertir la imagen del canvas (RGBA) a escala de grises
    img = canvas_result.image_data.astype(np.uint8)
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)

    # Redimensionar la imagen a 28x28 píxeles
    img_resized = cv2.resize(img_gray, (28, 28), interpolation=cv2.INTER_AREA)
    
    # Invertir colores para que el dígito sea blanco sobre fondo negro (formato MNIST)
    img_resized = 255 - img_resized

    # Normalizar la imagen
    img_norm = img_resized.astype("float32") / 255.0

    # Preparar la imagen para la predicción (añadir dimensiones)
    img_input = np.expand_dims(img_norm, axis=0)   # forma (1, 28, 28)
    img_input = np.expand_dims(img_input, axis=-1)   # forma (1, 28, 28, 1)

    # Realizar la predicción
    prediction = model.predict(img_input)
    predicted_digit = np.argmax(prediction)
    st.write("Predicción del modelo:", predicted_digit)

    # Mostrar la imagen procesada (opcional)
    st.image(img_resized, caption="Imagen procesada", width=140)

    # Crear botones de validación
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Correcto"):
            st.success("¡Genial! La predicción fue correcta.")
    with col2:
        if st.button("Incorrecto"):
            # Solicitar al usuario el valor correcto
            correct_label = st.text_input("Ingresa el valor correcto:", key="label")
            if correct_label != "":
                # Guardar la imagen para uso futuro (nuevos datos de entrenamiento)
                save_dir = "new_samples"
                os.makedirs(save_dir, exist_ok=True)
                sample_index = len(os.listdir(save_dir))
                sample_filename = os.path.join(save_dir, f"sample_{correct_label}_{sample_index}.png")
                cv2.imwrite(sample_filename, img_resized)
                st.error(f"Muestra guardada como {sample_filename}")
