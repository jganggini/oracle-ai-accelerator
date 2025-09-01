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


interface MyComponentProps extends ComponentProps {
  args: {
    disabled?: boolean
    language?: string
  }
}

function MyComponent({ args }: MyComponentProps) {
  const { disabled, language } = args
  const [isRecording, setIsRecording] = useState(false)
  const [hasRecorded, setHasRecorded] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const processorRef = useRef<ScriptProcessorNode | null>(null)

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
      if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
        wsRef.current.close();
        wsRef.current = null;
      }

      // const ws = new WebSocket(`${window.location.origin.replace("http", "ws")}/ws/audio`)
      const backendUrl =
        window.location.hostname === "localhost"
          ? "ws://localhost:8000/ws/audio"
          : `${window.location.origin.replace("http", "ws")}/ws/audio`;

      const ws = new WebSocket(backendUrl);
      wsRef.current = ws

      ws.onopen = () => {
        console.log("WebSocket abierto con idioma:", language);
        Streamlit.setComponentValue({ type: "start" });
        ws.send(JSON.stringify({ type: "start", language: language || "esa" }))
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
      const processor = audioContext.createScriptProcessor(2048, 1, 1);

      processor.onaudioprocess = (event) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          const input = event.inputBuffer.getChannelData(0);
          const pcm16 = floatTo16BitPCM(input);
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
  }, [language]) //  si cambia el idioma, lo reenvía al iniciar

  const stopRecording = useCallback(() => {
    try {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "stop" }));
        Streamlit.setComponentValue({ type: "stop" });
      }

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
    backgroundColor: active ? "#e53935" : "#1e1e1e",
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
      <button
        onClick={startRecording}
        disabled={disabled || isRecording}
        style={buttonStyle(!disabled && !isRecording)}
      >
        🎤 Start
      </button>
      <button
        onClick={stopRecording}
        disabled={disabled || !isRecording}
        style={buttonStyle(!disabled && isRecording)}
      >
        ⏹️ Stop
      </button>
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
