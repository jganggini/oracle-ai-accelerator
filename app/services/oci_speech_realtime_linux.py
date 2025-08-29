import asyncio
import os
from dotenv import load_dotenv
from oci.config import from_file
from oci_ai_speech_realtime import RealtimeSpeechClient, RealtimeSpeechClientListener
from oci.ai_speech.models import RealtimeParameters

# -----------------------------
# Cargar variables de entorno
# -----------------------------
load_dotenv()

language_map = {
    "esa": "es-ES",
    "ptb": "pt-BR",
    "gb": "en-GB"
}

audio_queue = None
client = None

# -----------------------------
# Parámetros de la sesión
# -----------------------------
def get_realtime_parameters(customizations, compartment_id, language_code):
    p = RealtimeParameters()
    p.language_code = language_code
    p.model_domain = RealtimeParameters.MODEL_DOMAIN_GENERIC
    p.partial_silence_threshold_in_ms = 0
    p.final_silence_threshold_in_ms = 2000
    p.encoding = "audio/raw;rate=16000"
    p.should_ignore_invalid_customizations = False
    p.stabilize_partial_results = RealtimeParameters.STABILIZE_PARTIAL_RESULTS_NONE
    p.punctuation = RealtimeParameters.PUNCTUATION_NONE
    return p

# -----------------------------
# Listener thread-safe
# -----------------------------
class MyListener(RealtimeSpeechClientListener):
    def __init__(self, on_final, on_partial):
        super().__init__()
        self.on_final = on_final
        self.on_partial = on_partial

    def on_result(self, result):
        #print("[DEBUG] on_result llamado con:", result)
        tx = result["transcriptions"][0]["transcription"]
        is_final = result["transcriptions"][0]["isFinal"]

        # Todo corre en el loop de fondo (thread-safe)
        loop = asyncio.get_event_loop()
        if is_final:
            asyncio.run_coroutine_threadsafe(self.on_final(tx), loop)
        else:
            asyncio.run_coroutine_threadsafe(self.on_partial(tx), loop)

    def on_ack_message(self, ackmessage):
        print("[DEBUG] on_ack_message:", ackmessage)
        return super().on_ack_message(ackmessage)

    def on_connect(self):
        print("[DEBUG] on_connect")
        return super().on_connect()

    def on_connect_message(self, connectmessage):
        print("[DEBUG] on_connect_message:", connectmessage)
        return super().on_connect_message(connectmessage)

    def on_network_event(self, netevent):
        print("[DEBUG] on_network_event:", netevent)
        return super().on_network_event(netevent)

    def on_error(self, error_message):
        print("[DEBUG][ERROR]", error_message)
        return super().on_error(error_message)

    def on_close(self, error_code, error_message):
        print(f"[DEBUG] on_close -> code={error_code}, msg={error_message}")

# -----------------------------
# Iniciar sesión de transcripción
# -----------------------------
async def start_realtime_session(display_transcription_final, display_transcription_partial, language):
    global client, audio_queue

    language_code = language_map.get(language)
    compartment_id = os.getenv("CON_COMPARTMENT_ID")
    service_endpoint = os.getenv("CON_SPEECH_SERVICE_ENDPOINT")
    customizations = []

    listener = MyListener(display_transcription_final, display_transcription_partial)
    config = from_file()

    audio_queue = asyncio.Queue()

    client = RealtimeSpeechClient(
        config=config,
        realtime_speech_parameters=get_realtime_parameters(customizations, compartment_id, language_code),
        listener=listener,
        service_endpoint=service_endpoint,
        compartment_id=compartment_id
    )

    async def send_audio_loop():
        while client and not client.close_flag:
            data = await audio_queue.get()
            if data:
                await client.send_data(data)

    # Conectar y lanzar loop de envío en paralelo
    await asyncio.gather(
        client.connect(),
        send_audio_loop()
    )

# -----------------------------
# Enviar audio desde el navegador
# -----------------------------
async def send_chunk_from_browser(audio_bytes: bytes):
    global audio_queue
    if audio_queue is None:
        raise RuntimeError("Audio queue no inicializada. Inicia primero la sesión.")
    await audio_queue.put(audio_bytes)
    #print(f"[OCI] Chunk agregado a queue: {len(audio_bytes)} bytes")

# -----------------------------
# Detener la sesión
# -----------------------------
async def stop_realtime_session():
    global client, audio_queue
    if client:
        client.close()
        client = None
    audio_queue = None
    print("[OCI] Sesión detenida")

