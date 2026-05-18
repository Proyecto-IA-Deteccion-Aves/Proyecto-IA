import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Clasificador de Aves IA", layout="centered")
st.title("🦅 Reconocedor y Clasificador de Aves")
st.write("Sube una imagen de un ave para identificar su especie basándose en el dataset CUB-200-2011.")

# 1. Cargar las clases (Nombres de las aves)
@st.cache_data
def load_classes():
    classes = []
    # Cargamos el archivo que contiene los nombres de las especies
    with open("classes.txt", "r") as f:
        for line in f:
            parts = line.strip().split(" ")
            if len(parts) == 2:
                # Extraemos el nombre limpiando los números y guiones bajos (ej: '001.Black_footed_Albatross' -> 'Black footed Albatross')
                name = parts[1].split(".")[-1].replace("_", " ")
                classes.append(name)
    return classes

bird_classes = load_classes()

# 2. Cargar los modelos guardados
@st.cache_resource
def load_models():
    m_reentrenado = tf.keras.models.load_model('birds_MobileNet.keras')
    m_final = tf.keras.models.load_model('birds_base.keras')
    m_final_v2 = tf.keras.models.load_model('birds_EfficientNetV2.keras')
    return m_reentrenado, m_final, m_final_v2

with st.spinner("Cargando modelos de inteligencia artificial..."):
    try:
        model_reentrenado, model_final, model_final_v2 = load_models()
    except Exception as e:
        st.error(f"Error al cargar los modelos: {e}")
        st.stop()

# 3. Subir imagen (A diferencia de dibujar números, para aves es mejor subir foto)
uploaded_file = st.file_uploader("Elige una imagen de un ave...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 4. Procesar la imagen visualmente para la interfaz
    image = Image.open(uploaded_file).convert('RGB')
    st.image(image, caption='Imagen subida', use_container_width=True)
    
    with st.spinner('Analizando el ave...'):

        target_size = (256, 256) 
        
        img = image.resize(target_size)
        img_array = np.array(img)
        
        img_array_v2 = np.expand_dims(img_array, axis=0) # Para EfficientNetV2S (NO normalizar a [0, 1])
        img_array_norm = img_array / 255.0 
        img_array_norm = np.expand_dims(img_array_norm, axis=0) # Para los modelos originales
        
        # 5. Predicción con los modelos
        pred_ree = model_reentrenado.predict(img_array_norm)[0]
        pred_fin = model_final.predict(img_array_norm)[0]
        pred_fin_v2 = model_final_v2.predict(img_array_v2)[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            clase_idx = np.argmax(pred_ree)
            confianza = pred_ree[clase_idx]
            animal_name = bird_classes[clase_idx] if clase_idx < len(bird_classes) else f"Clase desconocida ({clase_idx})"
            
            st.subheader("Model MobilenetV2 (birds_MobileNet)")
            st.markdown(f"**Especie:** {animal_name}")
            
            if confianza < 0.60:
                st.error(f"Confianza muy baja ({confianza:.2%})")
            elif confianza < 0.85:
                st.warning(f"Confianza moderada ({confianza:.2%})")
            else:
                st.success(f"Confianza alta: {confianza:.2%}")
                
            st.write("**Top 5 predicciones:**")
            top5_idx = np.argsort(pred_ree)[-5:][::-1]
            for i in top5_idx:
                nombre_clase = bird_classes[i] if i < len(bird_classes) else f"Clase {i}"
                st.write(f"- {nombre_clase}: {pred_ree[i]:.2%}")
                st.progress(float(pred_ree[i]))
                
        with col2:
            clase_idx2 = np.argmax(pred_fin)
            confianza2 = pred_fin[clase_idx2]
            animal_name2 = bird_classes[clase_idx2] if clase_idx2 < len(bird_classes) else f"Clase desconocida ({clase_idx2})"
            
            st.subheader("Modelo Base (birds_base)")
            st.markdown(f"**Especie:** {animal_name2}")
            
            if confianza2 < 0.60:
                st.error(f"Confianza muy baja ({confianza2:.2%})")
            elif confianza2 < 0.85:
                st.warning(f"Confianza moderada ({confianza2:.2%})")
            else:
                st.success(f"Confianza alta: {confianza2:.2%}")
                
            st.write("**Top 5 predicciones:**")
            top5_idx2 = np.argsort(pred_fin)[-5:][::-1]
            for i in top5_idx2:
                nombre_clase = bird_classes[i] if i < len(bird_classes) else f"Clase {i}"
                st.write(f"- {nombre_clase}: {pred_fin[i]:.2%}")
                st.progress(float(pred_fin[i]))
                
        with col3:
            clase_idx3 = np.argmax(pred_fin_v2)
            confianza3 = pred_fin_v2[clase_idx3]
            animal_name3 = bird_classes[clase_idx3] if clase_idx3 < len(bird_classes) else f"Clase desconocida ({clase_idx3})"
            
            st.subheader("Modelo EfficientNetV2S (birds_EfficientNetV2)")
            st.markdown(f"**Especie:** {animal_name3}")
            
            if confianza3 < 0.60:
                st.error(f"Confianza muy baja ({confianza3:.2%})")
            elif confianza3 < 0.85:
                st.warning(f"Confianza moderada ({confianza3:.2%})")
            else:
                st.success(f"Confianza alta: {confianza3:.2%}")
                
            st.write("**Top 5 predicciones:**")
            top5_idx3 = np.argsort(pred_fin_v2)[-5:][::-1]
            for i in top5_idx3:
                nombre_clase = bird_classes[i] if i < len(bird_classes) else f"Clase {i}"
                st.write(f"- {nombre_clase}: {pred_fin_v2[i]:.2%}")
                st.progress(float(pred_fin_v2[i]))
