import base64
import json
import asyncio
import platform 

from fastapi import FastAPI, WebSocket

is_linux   =  platform.system()  == "Linux"
is_windows =  platform.system()  == "Windows"

if is_linux:
    import services.oci_speech_realtime_linux as oci_realtime
elif is_windows:
    import services.oci_speech_realtime as oci_realtime

app = FastAPI()

# -----------------------------
# Endpoint WebSocket de audio
# -----------------------------
@app.get("/health")
async def health():
    return {"status": "ok"} 
    
@app.websocket("/ws/audio")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("[BACKEND] Cliente conectado")

    # Callbacks que OCI llamará cuando haya transcripción
    async def on_final(text: str):
        await ws.send_json({"type": "final", "text": text})

    async def on_partial(text: str):
        await ws.send_json({"type": "partial", "text": text})

    # Estado de la sesión
    session_task = None

    try:
        while True:
            msg = await ws.receive()
            #msg = await ws.receive_json()
      
            if isinstance(msg, dict) and msg.get("bytes") is not None:
                audio_bytes = msg.get("bytes")
                #print(f"[BACKEND] Chunk binario recibido, {len(audio_bytes)} bytes")
                # envia al wrapper OCI (asegúrate que acepta bytes PCM16)
                await oci_realtime.send_chunk_from_browser(audio_bytes)
                continue
            
            if isinstance(msg, dict) and msg.get("text") is not None:
                text_msg = msg["text"]
                try:
                    data = json.loads(text_msg)
                except json.JSONDecodeError:
                    print("[BACKEND] Texto recibido no es JSON válido:", text_msg[:200])
                    continue

                msg_type = data.get("type")
                print("[BACKEND] JSON decodificado:", data)


                if msg_type == "start" and session_task is None:
                    # Iniciar sesión OCI
                    print("[BACKEND] Iniciando sesión OCI...")
                    await ws.send_json({"type": "start"})
                    session_task = asyncio.create_task(
                        oci_realtime.start_realtime_session(
                            on_final,
                            on_partial,
                            language="esa"  
                        )
                    )
                    
                    
                elif msg_type == "chunk":
                    audio_bytes = base64.b64decode(msg["data"])
                    await oci_realtime.send_chunk_from_browser(audio_bytes)

                elif msg_type == "stop":
                    print("[BACKEND] Stop recibido")
                    await ws.send_json({"type": "stop"})
                    await oci_realtime.stop_realtime_session()
                    if session_task:
                        session_task.cancel()
                        session_task = None
                    

                elif msg_type == "reset":
                    print("[BACKEND] Reset recibido")
                    await oci_realtime.stop_realtime_session()
                    if session_task:
                        session_task.cancel()
                        session_task = None
                    await ws.send_json({"type": "reset"})

    except Exception as e:
        print(f"[BACKEND] Error WebSocket: {e}")
    finally:
        if session_task:
            session_task.cancel()
        await oci_realtime.stop_realtime_session()
        print("[BACKEND] Cliente desconectado")
