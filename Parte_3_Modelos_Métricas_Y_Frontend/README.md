# 🦅 Clasificador de Aves IA - Guía de Despliegue

Esta guía te explicará paso a paso cómo construir y ejecutar la aplicación de clasificación de aves (basada en Streamlit y TensorFlow) utilizando Docker.

## ⚠️ Nota Importante sobre los Modelos

Debido al tamaño elevado de los archivos resultantes del entrenamiento (modelos `.keras`), estos exceden los límites de tamaño permitidos por GitHub. Por ello, **los modelos están adjuntados en un archivo `.zip` en la entrega de la práctica**. 

Por favor, asegúrate de descomprimir ese archivo `.zip` y colocar los tres modelos (`birds_reentrenado.keras`, `birds_final.keras` y `birds_final_v2.keras`) directamente en esta misma carpeta (junto al archivo `app.py`) antes de seguir los pasos de esta guía.

## 📋 Requisitos Previos

* Tener [Docker](https://www.docker.com/products/docker-desktop/) instalado y ejecutándose en tu máquina (por ejemplo, Docker Desktop).

## 🚀 1. Construir la Imagen de Docker

Abre tu terminal, navega hasta esta carpeta (`proyecto-ia`) donde se encuentra el archivo `Dockerfile`, y ejecuta el siguiente comando para construir la imagen. Esto descargará Python y todas las dependencias necesarias.

```bash
docker build -t app-clasificador-aves .
```

*Nota: La primera vez que ejecutes este comando puede tardar un poco debido a que debe descargar librerías pesadas como TensorFlow.*

## 🏃 2. Ejecutar el Contenedor

Una vez que la imagen ha terminado de compilarse, debes montar y ejecutar el contenedor y exponer el puerto `8501`, que es el que utiliza Streamlit por defecto.

```bash
docker run -d -p 8501:8501 --name aves-container app-clasificador-aves
```

* `-d`: Ejecuta el contenedor en segundo plano (detached).
* `-p 8501:8501`: Conecta el puerto 8501 de tu computadora con el puerto 8501 del contenedor.
* `--name aves-container`: Le da un nombre amigable a tu contenedor.

## 🌐 3. Ver la Aplicación

Abre tu navegador web favorito y visita la siguiente dirección:

**[http://localhost:8501](http://localhost:8501)**

¡Ya deberías estar viendo la interfaz de Streamlit lista para clasificar aves!

---

## 🛠️ Truco para Desarrollo (No reconstruir la imagen)

Si quieres hacer cambios en el archivo `app.py` y verlos reflejados inmediatamente **sin tener que reconstruir la imagen de Docker entera**, puedes usar un **volumen**. Primero borra el contenedor anterior si lo tenías:

```bash
docker rm -f aves-container
```

Y luego arráncalo conectando tu carpeta actual al interior del contenedor:

```bash
# En Linux/Mac:
docker run -d -p 8501:8501 -v $(pwd):/app --name aves-container app-clasificador-aves

# En Windows (PowerShell):
docker run -d -p 8501:8501 -v ${PWD}:/app --name aves-container app-clasificador-aves
```

Ahora, cada vez que guardes un cambio en `app.py`, simplemente recarga la página en tu navegador (`localhost:8501`) y verás tu nueva versión funcionando.
