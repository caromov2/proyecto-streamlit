import streamlit as st
import requests
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURACIÓN ---
SPEECH_KEY = st.secrets["SPEECH_KEY"]
TRANSLATOR_KEY = st.secrets["TRANSLATOR_KEY"]
STT_URL = st.secrets["STT_URL"]
TTS_URL = st.secrets["TTS_URL"]
TRANS_URL = st.secrets["TRANS_URL"]

# --- INTERFAZ ---
st.title("🎤 Traductor Multilingüe")
st.markdown("---")

# Diccionario de idiomas y voces
idiomas = {
    "Español": "es-ES",
    "Inglés": "en-US",
    "Francés": "fr-FR",
    "Alemán": "de-DE",
    "Italiano": "it-IT",
    "Portugués (Brasil)": "pt-BR" 
}

voces_disponibles = {
    "es-ES": ["es-ES-ElviraNeural", "es-ES-AlvaroNeural"],
    "en-US": ["en-US-JennyNeural", "en-US-GuyNeural"],
    "fr-FR": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"],
    "de-DE": ["de-DE-KatjaNeural", "de-DE-ConradNeural"],
    "it-IT": ["it-IT-ElsaNeural", "it-IT-IsabellaNeural"],
    "pt-BR": ["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural"]  
    
}

# --- SELECTORES DE IDIOMA ---
col1, col2 = st.columns(2)
with col1:
    idioma_origen = st.selectbox("🌍 Idioma de origen", list(idiomas.keys()))
with col2:
    idioma_destino = st.selectbox("🌎 Idioma destino", list(idiomas.keys()))

codigo_origen = idiomas[idioma_origen]
codigo_destino = idiomas[idioma_destino]

voz_destino = st.selectbox(f"🗣️ Voz para {idioma_destino}", voces_disponibles[codigo_destino])


# --- AUDIO ---
st.header("🎙️ Entrada de audio")
col_mic, col_file = st.columns(2)

with col_mic:
    grabacion_data = mic_recorder("Grabar", "Detener", just_once=True, key="recorder")
with col_file:
    uploaded = st.file_uploader("Sube un archivo WAV/WEBM", type=["wav", "webm"])

audio_data = None

if uploaded:
    audio_data = uploaded.getbuffer().tobytes()
    st.success(f"Archivo cargado: {uploaded.name}")
    st.audio(audio_data,format="audio/wav")
elif grabacion_data and grabacion_data.get("bytes"):
    audio_data = grabacion_data["bytes"]
    st.success("Grabación completada ✅")
    st.audio(audio_data,format="audio/wav")


# --- STT ---
if audio_data:
    st.markdown("---")
    st.header("🧠 Transcripción de Voz")

    params = {"language": codigo_origen, "format": "simple"}
    headers_stt = {
        "Ocp-Apim-Subscription-Key": SPEECH_KEY,
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        "Accept": "application/json"
    }
    
    try:
        resp = requests.post(STT_URL, params=params, headers=headers_stt, data=audio_data)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error STT: {e}")
        st.stop()

    data = resp.json()
    texto = data.get("DisplayText") or data.get("Text")
    if not texto:
        st.warning("⚠️ No se detectó texto en el audio.")
        st.stop()
    
    st.success(f"📝 **Texto transcrito:** {texto}")

    # --- TRADUCCIÓN ---
    st.markdown("---")
    st.header("🌐 Traducción")
    trans_params = {"api-version": "3.0", "from": codigo_origen, "to": [codigo_destino]}
    
    headers_tr = {
        "Ocp-Apim-Subscription-Key": TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": "germanywestcentral",
        "Content-Type": "application/json"
    }
    body = [{"text": texto}]
    tr_resp = requests.post(TRANS_URL, params=trans_params, headers=headers_tr, json=body)
    if tr_resp.status_code == 200:
        texto_tradu = tr_resp.json()[0]['translations'][0]['text']
        st.success(f"💬 **Traducción al {idioma_destino}:** {texto_tradu}")
    else:
        st.error(f"❌ Error traducción: {tr_resp.text[:300]}")
        st.stop()

    # --- TTS ---
    st.markdown("---")
    st.header("🔊 Síntesis de voz (TTS)")
    ssml = f"""
    <speak version='1.0' xml:lang='{codigo_destino}'>
        <voice name='{voz_destino}'>{texto_tradu}</voice>
    </speak>"""
    headers_tts = {
        "Ocp-Apim-Subscription-Key": SPEECH_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3"
    }
    tts_resp = requests.post(TTS_URL, headers=headers_tts, data=ssml.encode("utf-8"))
    if tts_resp.status_code == 200:
        st.audio(tts_resp.content, format="audio/mp3")
        st.success(f"🔉 **Voz generada con:** {voz_destino}")
    else:
        st.error(f"❌ Error TTS: {tts_resp.text[:300]}")
else:
    st.info("🎧 Sube o graba un audio para comenzar.")
