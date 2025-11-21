import asyncio
import os
import av
from dotenv import load_dotenv
from oci.config import from_file
from oci_ai_speech_realtime import RealtimeSpeechClient, RealtimeSpeechClientListener
from oci.ai_speech.models import RealtimeParameters
from streamlit_webrtc import AudioProcessorBase
import streamlit as st

language_map = {
    "Spanish"    : "es-ES",
    "Portuguese" : "pt-BR",
    "English"    : "en-GB"
}

load_dotenv()

SAMPLE_RATE = 16000
CHANNELS = 1
BUFFER_DURATION_MS = 96

def get_realtime_parameters(customizations, compartment_id, language_code):
    """Configure OCI Speech Realtime parameters"""
    realtime_speech_parameters = RealtimeParameters()
    realtime_speech_parameters.language_code = language_code
    realtime_speech_parameters.model_domain = RealtimeParameters.MODEL_DOMAIN_GENERIC
    realtime_speech_parameters.partial_silence_threshold_in_ms = 0
    realtime_speech_parameters.final_silence_threshold_in_ms = 2000
    realtime_speech_parameters.encoding = f"audio/raw;rate={SAMPLE_RATE}"
    realtime_speech_parameters.should_ignore_invalid_customizations = False
    realtime_speech_parameters.stabilize_partial_results = RealtimeParameters.STABILIZE_PARTIAL_RESULTS_NONE
    realtime_speech_parameters.punctuation = RealtimeParameters.PUNCTUATION_NONE

    for customization_id in customizations:
        realtime_speech_parameters.customizations = [
            {
                "compartmentId": compartment_id,
                "customizationId": customization_id,
            }
        ]

    return realtime_speech_parameters

class OCIAudioProcessor(AudioProcessorBase):
    """WebRTC Audio Processor for OCI Speech"""
    def __init__(self):
        self.audio_queue = None
        self.resampler = av.AudioResampler(format="s16", layout="mono", rate=16000)

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        if self.audio_queue is None:
            return frame
        
        try:
            resampled_frames = self.resampler.resample(frame)
            for resampled_frame in resampled_frames:
                data = resampled_frame.to_ndarray().tobytes()
                self.audio_queue.put(data)
        except Exception:
            pass
        
        return frame

class MyListener(RealtimeSpeechClientListener):
    """OCI Speech Realtime Client Listener"""
    def __init__(self, display_transcription_final, display_transcription_partial):
        super().__init__()
        self.display_transcription_final = display_transcription_final
        self.display_transcription_partial = display_transcription_partial
    
    def on_result(self, result):
        if result["transcriptions"][0]["isFinal"]:
            transcription = result['transcriptions'][0]['transcription']
            self.display_transcription_final(transcription)
        else:
            transcription = result['transcriptions'][0]['transcription']
            self.display_transcription_partial(transcription)

    def on_ack_message(self, ackmessage):
        """Handle server acknowledgment messages"""
        pass

    def on_connect(self):
        """Handle successful connection event"""
        pass

    def on_connect_message(self, connectmessage):
        """Handle server connection message"""
        pass

    def on_network_event(self, event):
        """Handle network events"""
        pass

    def on_error(self, error_message):
        """Handle error messages"""
        pass

    def on_close(self, error_code, error_message):
        """Handle connection close"""
        pass

async def start_realtime_session(display_transcription_final, display_transcription_partial, language, input_queue):
    """
    Manages OCI Speech Realtime session with auto-reconnect logic.
    Waits for audio data before connecting to avoid idle timeouts.
    """
    language = language_map.get(language)
    customizations = []
    compartment_id = os.getenv("CON_COMPARTMENT_ID")
    language_code = language
    service_endpoint = os.getenv("CON_SPEECH_SERVICE_ENDPOINT")
    config = from_file()

    while True:
        first_packet = await input_queue.get()
        
        if first_packet is None:
            break

        listener = MyListener(display_transcription_final, display_transcription_partial)
        realtime_speech_parameters = get_realtime_parameters(
            customizations=customizations,
            compartment_id=compartment_id,
            language_code=language_code
        )

        client = RealtimeSpeechClient(
            config=config,
            realtime_speech_parameters=realtime_speech_parameters,
            listener=listener,
            service_endpoint=service_endpoint,
            compartment_id=compartment_id
        )

        st.session_state.speech_client = client

        async def send_audio_loop(client_ref, initial_packet):
            try:
                if not client_ref.close_flag:
                    await client_ref.send_data(initial_packet)
                
                while not client_ref.close_flag:
                    data = await input_queue.get()
                    if data is None:
                        client_ref.close()
                        break
                    await client_ref.send_data(data)
                    
            except asyncio.CancelledError:
                client_ref.close()
            except Exception:
                client_ref.close()

        send_task = asyncio.create_task(send_audio_loop(client, first_packet))

        try:
            await client.connect()
        except Exception:
            pass

        if not send_task.done():
            send_task.cancel()
            try:
                await send_task
            except:
                pass

def stop_realtime_session():
    """Stop the current realtime session"""
    client = st.session_state.get("speech_client")
    if client:
        client.close()
        st.session_state.speech_client = None
