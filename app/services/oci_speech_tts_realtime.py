import oci
import os
from oci.ai_speech.models import SynthesizeSpeechDetails, TtsOracleConfiguration, TtsOracleTts2NaturalModelDetails, TtsOracleSpeechSettings

# --- TTS Configuration ---
# We can make these configurable via .env if needed later
VOICE_ID = "Mateo"
OUTPUT_FORMAT = TtsOracleSpeechSettings.OUTPUT_FORMAT_MP3
SAMPLE_RATE = 24000
# -------------------------

def get_speech_client():
    """
    Creates and returns an OCI AI Speech Service client.
    It reuses the default OCI config file (~/.oci/config).
    """
    config = oci.config.from_file()
    # Use the TTS endpoint from environment variables
    endpoint = os.getenv('CON_SPEECH_SERVICE_TTS_ENDPOINT')
    
    # We create a signer from the default config file
    signer = oci.signer.Signer(
        tenancy=config["tenancy"],
        user=config["user"],
        fingerprint=config["fingerprint"],
        private_key_file_location=config["key_file"]
    )
    
    return oci.ai_speech.AIServiceSpeechClient(config, signer=signer, service_endpoint=endpoint)

def text_to_speech(text_to_synthesize: str):
    """
    Synthesizes text into speech using OCI TTS and returns the audio as bytes.

    Args:
        text_to_synthesize: The text to be converted to speech.

    Returns:
        The audio data as bytes (in MP3 format), or None if an error occurs.
    """
    try:
        client = get_speech_client()
        compartment_id = os.getenv('CON_COMPARTMENT_ID')

        if not compartment_id:
            return None

        payload = SynthesizeSpeechDetails(
            text=text_to_synthesize,
            compartment_id=compartment_id,
            configuration=TtsOracleConfiguration(
                model_details=TtsOracleTts2NaturalModelDetails(voice_id=VOICE_ID,language_code="es-ES"),
                speech_settings=TtsOracleSpeechSettings(
                    sample_rate_in_hz=SAMPLE_RATE,
                    output_format=OUTPUT_FORMAT
                )
            )
        )
        
        response = client.synthesize_speech(payload)

        if response.status == 200:
            # The response.data is a stream. We need to read it into memory.
            audio_bytes = b"".join(chunk for chunk in response.data.iter_content())
            return audio_bytes
        else:
            return None
            
    except Exception as e:
        return None
