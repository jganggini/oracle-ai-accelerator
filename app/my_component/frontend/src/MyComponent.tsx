import { Streamlit, withStreamlitConnection, ComponentProps } from "streamlit-component-lib"
import React, { useState, useEffect, useRef, useCallback } from "react"
import '../public/streamlit-buttons.css';

function floatTo16BitPCM(float32Array: Float32Array): Uint8Array {
  const buffer = new ArrayBuffer(float32Array.length * 2)
  const view = new DataView(buffer)
  let offset = 0
  for (let i = 0; i < float32Array.length; i++, offset += 2) {
    let s = Math.max(-1, Math.min(1, float32Array[i]))
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true)
  }
  return new Uint8Array(buffer)
}

function MyComponent({ disabled }: ComponentProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [hasRecorded, setHasRecorded] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const processorRef = useRef<ScriptProcessorNode | null>(null)

  // useEffect(() => {
  //   Streamlit.setFrameHeight()
  //   return () => stopRecording()
  // }, [])

    // Cerrar socket al desmontar el componente
    useEffect(() => {
      Streamlit.setFrameHeight();
      return () => {
        stopRecording();
        if (wsRef.current) {
          wsRef.current.close();
          wsRef.current = null;
        }
      };
    }, []);
  

  const startRecording = useCallback(async () => {
    try {
      // Cerrar socket viejo si existe
      if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
        wsRef.current.close();
        wsRef.current = null;
      }

      const ws = new WebSocket("ws://localhost:8000/ws/audio")
      wsRef.current = ws

      ws.onopen = () => {
        console.log("WebSocket abierto");
        Streamlit.setComponentValue({ type: "start" });
        ws.send(JSON.stringify({ type: "start" }))
      }

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data)
        Streamlit.setComponentValue(msg)
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaStreamRef.current = stream
      const audioContext = new AudioContext({ sampleRate: 16000 })
      audioContextRef.current = audioContext

      const source = audioContext.createMediaStreamSource(stream)
      // const processor = audioContext.createScriptProcessor(4096, 1, 1)

      // processor.onaudioprocess = (e) => {
      //   const input = e.inputBuffer.getChannelData(0)
      //   const pcm16 = floatTo16BitPCM(input)
      //   const b64 = btoa(String.fromCharCode(...pcm16))
      //   ws.send(JSON.stringify({ type: "chunk", data: b64 }))
      // }

      const processor = audioContext.createScriptProcessor(2048, 1, 1);

      processor.onaudioprocess = (event) => {
        //console.log("Processing audio chunk...");
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          const input = event.inputBuffer.getChannelData(0);
          const pcm16 = floatTo16BitPCM(input);
          // Enviar como binario en vez de JSON/base64
          wsRef.current.send(pcm16.buffer);
        }
      };

      source.connect(processor)
      processor.connect(audioContext.destination)
      processorRef.current = processor

      setIsRecording(true)
      setHasRecorded(true)
    } catch (err) {
      console.error("Error starting recording:", err)
    }
  }, [])

  const stopRecording = useCallback(() => {
    try {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "stop" }));
        Streamlit.setComponentValue({ type: "stop" });
      }

      // wsRef.current?.send(JSON.stringify({ type: "stop" }))
      // wsRef.current?.close()
      // wsRef.current = null

      processorRef.current?.disconnect()
      processorRef.current = null
      audioContextRef.current?.close()
      audioContextRef.current = null
      mediaStreamRef.current?.getTracks().forEach((t) => t.stop())
      mediaStreamRef.current = null

      setIsRecording(false)
    } catch (err) {
      console.error("Error stopping recording:", err)
    }
  }, [])

  const resetRecording = useCallback(() => {
    try {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "reset" }));
      }
      wsRef.current?.close();
      wsRef.current = null;

      setHasRecorded(false);
      Streamlit.setComponentValue({ type: "reset" });
    } catch (err) {
      console.error("Error resetting recording:", err);
    }
  }, []);
  

  const buttonStyle = (active: boolean) => ({
    backgroundColor: active ? "#e53935" : "#1e1e1e", // rojo si activo, negro si no
    color: "white",
    padding: "10px 28px",
    border: "none",
    borderRadius: "6px",
    cursor: active ? "pointer" : "not-allowed",
    fontSize: "14px",
    fontWeight: 500,
    minWidth: "100px",
  })

  return (
    <div style={{ display: "flex", gap: "10px" }}>
      {/* Start */}
      <button
        onClick={startRecording}
        disabled={disabled || isRecording}
        style={buttonStyle(!disabled && !isRecording)}
      >
        🎤 Start
      </button>

      {/* Stop */}
      <button
        onClick={stopRecording}
        disabled={disabled || !isRecording}
        style={buttonStyle(!disabled && isRecording)}
      >
        ⏹️ Stop
      </button>

      {/* Reset */}
      <button
        onClick={resetRecording}
        disabled={disabled || isRecording || !hasRecorded}
        style={buttonStyle(!disabled && !isRecording && hasRecorded)}
      >
        🔄 Reset
      </button>
    </div>
  )
}
export default withStreamlitConnection(MyComponent)

