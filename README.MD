from pathlib import Path

# Texto corregido del README.md
readme_text = """# 🌍 Traductor Multilingüe con Voz

Proyecto elegido: **Traductor multilingüe con voz (voz → texto → traducción → voz)**  

Para el tema de seguridad, he usado `st.secrets` de Streamlit, evitando exponer las claves en el código fuente.

Imports necesarios:  
`import streamlit as st`, `import requests`, `from streamlit_mic_recorder import mic_recorder`

## Índice

1. [Descripción del Proyecto](#descripción-del-proyecto)  
2. [Tecnologías y APIs utilizadas](#tecnologías-y-apis-utilizadas)  
   - [1. Azure Speech-to-Text (STT)](#1-azure-speech-to-text-stt)  
   - [2. Azure Translator](#2-azure-translator)  
   - [3. Azure Text-to-Speech (TTS)](#3-azure-text-to-speech-tts)  
3. [Funcionalidades de la Aplicación](#funcionalidades-de-la-aplicación)  
4. [Funcionamiento del Código](#4-cómo-funciona-el-código)

---

## Descripción del Proyecto

Esta aplicación permite a los usuarios grabar o subir un audio y obtener:

1. **Transcripción del audio a texto**  
2. **Traducción del texto a otro idioma**  
3. **Síntesis de voz del texto traducido**

El flujo completo se realiza usando **APIs de Azure**, proporcionando un procesamiento de voz y lenguaje rápido y confiable.

---

## Tecnologías y APIs utilizadas

Se han utilizado las APIs de Azure, concretamente:

### 1. Azure Speech-to-Text (STT)
- Convierte la voz en texto usando modelos neuronales de Azure.  
- Permite seleccionar el idioma de origen para mejorar la precisión.  
- Configuración de audio: WAV o WEBM, 16 kHz, PCM.  
- Proporciona transcripción rápida y precisa de contenido hablado.  

### 2. Azure Translator
- Traduce el texto transcrito a cualquier idioma compatible con Azure.  
- Configurado con la versión `3.0` de la API.  
- Permite traducción bidireccional manteniendo la coherencia semántica.  
- Ideal para comunicación multilingüe instantánea.  

### 3. Azure Text-to-Speech (TTS)
- Convierte el texto traducido en voz de alta calidad.  
- Permite elegir la voz y el idioma de salida (por ejemplo, `ElviraNeural`, `JennyNeural`).  
- Genera salida en formato MP3, compatible con la mayoría de plataformas.  
- Facilita la creación de contenido accesible y multilingüe.  

---

## Funcionalidades de la Aplicación

- Interfaz **intuitiva y responsiva** creada con Streamlit.  
- Grabación de audio directamente desde el navegador o carga de archivos existentes.  
- Selección de idiomas de origen y destino, con voces configurables.  
- Manejo de errores para cada API, mostrando mensajes claros al usuario.  

---

## 4. Cómo funciona el código

Esta sección explica cómo se procesa la entrada de audio en la aplicación.

![Diagrama del flujo de audio](capturas/captura1.png)

### — Selector de idioma —
Tenemos dos columnas:  
- **col1**: selector del idioma de origen, con un array de idiomas disponibles.  
- **col2**: selector del idioma de destino.

### — Audio —
Disponemos de dos columnas con opciones para:
- **Grabar audio** usando `mic_recorder` (que se importa en el código).  
- **Subir un archivo** mediante `file_uploader`.

1. Se inicializa `audio_data` como `None`.  
2. Si el usuario sube un archivo, se convierte a bytes y se guarda en `audio_data`.  
   - `uploaded` es el nombre del archivo subido.  
   - `grabacion_data` es la grabación realizada con el micrófono.  
3. Si el usuario graba audio con el micrófono, también se guarda en `audio_data`.  
4. Se muestra un mensaje de éxito indicando que el audio está listo para procesarse.

![Captura STT, traducción](capturas/captura2.png)

### — STT —
Tenemos una condición `if` donde se ejecuta el bloque solo si `audio_data` contiene algo.

- En `params` definimos los parámetros de consulta, especificando el idioma de origen y el formato.  
- En `headers_stt` se definen los parámetros de autenticación y tipo de contenido.  
  - En `Content-Type` se indica que el formato es audio WAV con codificación PCM a 16.000 Hz.  
  - En `Accept` se especifica que la respuesta será en formato JSON.  
- En `resp` enviamos la solicitud POST con todos los parámetros.  
- Con `raise_for_status()` comprobamos si hay errores de código de estado.  
- Si hay error, se muestra un mensaje en el bloque `except`.  
- Guardamos el contenido devuelto en `data` en formato JSON.  
- Comprobamos si devuelve el texto transcrito; si funciona, se muestra con `st.success()` el texto obtenido del JSON.

---

### — Traducción —
En esta sección enviamos el texto transcrito al servicio de traducción.

- Para ello usamos `trans_params`, donde especificamos los parámetros necesarios: versión de la API, idioma de origen y destino.  
- En el encabezado (`headers`) se envía la clave, la región y el formato de salida (JSON).  
- En el `body` se crea el contenido de la solicitud JSON, una lista con un diccionario que contiene el texto a traducir.  
- En `tr_resp` enviamos la solicitud POST.  
- Comprobamos si devuelve algún error; si el código de estado es 200, extraemos del JSON el texto traducido.

![Captura TTS](capturas/captura3.png)

---

### — TTS —

Aqui en esta seccion queremos enviar el texto traducido para crear un audio con el idioma seleccionado.

ssml = f"""...""": Crea el Speech Synthesis Markup Language (SSML). El SSML es un formato XML que instruye al servicio de TTS sobre cómo debe generarse la voz.

    <speak version='1.0' xml:lang='{codigo_destino}'>: Define el idioma base para la síntesis, utilizando el código del idioma destino.

    <voice name='{voz_destino}'>{texto_tradu}</voice>: Especifica la voz a utilizar (voz_destino) y encierra el texto a leer (texto_tradu).

En el headers_tts enviamos la key el ssml y el formato del audio que es MP3, mono, 16kHz, 128kbps.

enviamos el post en tts_resp y comprovamos el status_code si es igual a 200 sacamos el audio y sinos sacamos el error  
