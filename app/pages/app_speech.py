import streamlit as st
import streamlit.components.v1 as st_components
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

import asyncio
import threading
import queue
import time
import json
import base64
from datetime import datetime

# Import components and services
import components as component
import services.database as database
import services as service
from services.oci_speech_stt_realtime import start_realtime_session, OCIAudioProcessor
from services.oci_speech_tts_realtime import text_to_speech

# Language mapping
LANGUAGE_MAP = {
    "Spanish": "es-ES",
    "Portuguese": "pt-BR",
    "English": "en-GB"
}

# Constants
MAX_PROCESSING_LOOPS = 100
LOOP_SLEEP_TIME = 0.05
RTC_ICE_SERVERS = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}

# Initialize services
db_agent_service = database.AgentService()
generative_service = service.GenerativeAIService()
select_ai_service = service.SelectAIService()
db_select_ai_service = database.SelectAIService()

# Load login and footer components
st.session_state["page"] = "app_speech.py"
login = component.get_login()
component.get_footer()


def initialize_session_state():
    """Initialize all session state variables for voice chat"""
    defaults = {
        "speech_conversation": [],
        "speech_audio_queue": queue.Queue(),
        "speech_result_queue": queue.Queue(),
        "speech_session_id": 0,
        "speech_llm_queue": queue.Queue(),
        "speech_processing_llm": False,
        "speech_current_partial": "",
        "speech_was_playing": False,
        "speech_autoplay_id": None,  # ID of the message that should autoplay
        "speech_playing_audio_id": None,  # ID of audio currently playing
        "speech_playing_audio_time": 0.0  # Current playback time
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_conversation(container, partial_text=None):
    """Render conversation using module 6 HTML style"""
    conversation_html = ""
    
    # Track last assistant message for autoplay
    last_assistant_idx = -1
    for i in range(len(st.session_state.speech_conversation) - 1, -1, -1):
        if st.session_state.speech_conversation[i]["role"] == "assistant":
            last_assistant_idx = i
            break
    
    for idx, item in enumerate(st.session_state.speech_conversation):
        if item['role'] == 'user':
            # User message style
            conversation_html += f"""
                <div style="background-color:#21232B; padding:10px; border-radius:5px; margin-bottom:10px; position:relative;">
                    <div style="display:flex; justify-content:space-between;">
                        <div style="width:35px; background-color:#4A9EFF; color:white; border-radius:5px; margin:2px; display:flex; align-items:center; justify-content:center; font-weight:bold;">
                            {idx + 1}</div>
                        <div style="width:100%; margin:2px; padding:5px; padding-bottom:20px;">
                            <div>{item['content']}</div>
                            <div style="position:absolute; bottom:5px; right:10px; color:#888; font-size:0.8em;">
                                {item['timestamp']}
                            </div>
                        </div>
                    </div>
                </div>
            """
        else:
            # Assistant message style
            # Get message ID (using timestamp as unique identifier)
            msg_id = item.get('timestamp', '')
            should_autoplay = (msg_id == st.session_state.speech_autoplay_id)
            
            audio_button = ""
            if item.get('audio'):
                audio_id = f"audio_{idx}"
                button_id = f"btn_{idx}"
                
                audio_button = f"""
                    <audio id="{audio_id}" {'autoplay' if should_autoplay else ''} style="display:none;">
                        <source src="data:audio/mp3;base64,{item['audio']}" type="audio/mp3">
                    </audio>
                    <span id="{button_id}" onclick="
                        var audio = document.getElementById('{audio_id}');
                        var btn = document.getElementById('{button_id}');
                        if (audio.paused) {{
                            audio.play();
                            btn.textContent = 'pause';
                        }} else {{
                            audio.pause();
                            btn.textContent = 'play_arrow';
                        }}
                    " class="material-symbols-rounded" style="
                        font-size: 20px;
                        color: #E6A538;
                        cursor: pointer;
                        margin-right: 8px;
                        vertical-align: middle;
                        user-select: none;
                    ">{'pause' if should_autoplay else 'play_arrow'}</span>
                    <script>
                        (function() {{
                            var audio = document.getElementById('{audio_id}');
                            var btn = document.getElementById('{button_id}');
                            
                            // When audio ends, reset button
                            audio.addEventListener('ended', function() {{
                                btn.textContent = 'play_arrow';
                            }});
                            
                            // When audio plays, update button
                            audio.addEventListener('play', function() {{
                                btn.textContent = 'pause';
                            }});
                            
                            // When audio pauses, update button
                            audio.addEventListener('pause', function() {{
                                btn.textContent = 'play_arrow';
                            }});
                        }})();
                    </script>
                """
            
            conversation_html += f"""
                <div style="background-color:#21232B; padding:10px; border-radius:5px; margin-bottom:10px; position:relative;">
                    <div style="display:flex; justify-content:space-between;">
                        <div style="width:35px; background-color:#E6A538; color:black; border-radius:5px; margin:2px; display:flex; align-items:center; justify-content:center; font-weight:bold;">
                            {idx + 1}</div>
                        <div style="width:100%; margin:2px; padding:5px; padding-bottom:20px;">
                            <div>{item['content']}</div>
                            <div style="position:absolute; bottom:5px; right:10px; color:#888; font-size:0.8em; display:flex; align-items:center;">
                                {audio_button}
                                {item['timestamp']}
                            </div>
                        </div>
                    </div>
                </div>
            """
    
    # Add global script to preserve audio state continuously
    preserve_audio_script = """
        <script>
            (function() {{
                // Continuously preserve audio state (runs every 200ms)
                setInterval(function() {{
                    var allAudios = document.querySelectorAll('audio');
                    var playingAudio = null;
                    var playingTime = 0;
                    
                    for (var i = 0; i < allAudios.length; i++) {{
                        var audio = allAudios[i];
                        if (!audio.paused && !audio.ended) {{
                            playingAudio = audio.id;
                            playingTime = audio.currentTime;
                            break;
                        }}
                    }}
                    
                    // Store in sessionStorage to persist across reruns
                    if (playingAudio) {{
                        sessionStorage.setItem('speech_playing_audio_id', playingAudio);
                        sessionStorage.setItem('speech_playing_audio_time', playingTime.toString());
                    }} else {{
                        // Clear if no audio is playing
                        sessionStorage.removeItem('speech_playing_audio_id');
                        sessionStorage.removeItem('speech_playing_audio_time');
                    }}
                }}, 200);
            }})();
        </script>
    """
    
    # Show partial transcription indicator (maintains until response is received)
    if partial_text:
        conversation_html += f"""
            <div style="background-color:#2A2A2A; padding:10px; border-radius:5px; margin-bottom:10px; opacity:0.6;">
                <div style="display:flex; justify-content:space-between;">
                    <div style="width:35px; background-color:#AAAAAA; color:black; border-radius:5px; margin:2px; display:flex; align-items:center; justify-content:center;">
                        •••</div>
                    <div style="width:100%; margin:2px; padding:5px;">
                        <div style="font-style:italic;">{partial_text}</div>
                    </div>
                </div>
            </div>
        """
    
    with container.container(border=True):
        st.markdown(":speech_balloon: :red[Real-Time] ***Voice Conversation***")
        st_components.html(f"""
            <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
            <div id="scrollable-conversation" style="height:400px; overflow-y:auto; background-color:#1e1e1e; padding:10px; border-radius:10px; color:white; font-family:monospace;">
                {conversation_html}
            </div>
            {preserve_audio_script}
            <script>
                // Restore audio playback state after rerun
                (function() {{
                    var savedAudioId = sessionStorage.getItem('speech_playing_audio_id');
                    var savedAudioTime = sessionStorage.getItem('speech_playing_audio_time');
                    
                    if (savedAudioId && savedAudioTime) {{
                        setTimeout(function() {{
                            var audio = document.getElementById(savedAudioId);
                            if (audio) {{
                                audio.currentTime = parseFloat(savedAudioTime);
                                audio.play().catch(function(e) {{
                                    // Autoplay might be blocked, that's ok
                                }});
                                // Clear saved state after restoring
                                sessionStorage.removeItem('speech_playing_audio_id');
                                sessionStorage.removeItem('speech_playing_audio_time');
                            }}
                        }}, 100);
                    }}
                }})();
                
                // Auto-scroll
                var div = window.parent.document.querySelectorAll('iframe[srcdoc]')[window.parent.document.querySelectorAll('iframe[srcdoc]').length - 1].contentWindow.document.getElementById('scrollable-conversation');
                if (div) div.scrollTop = div.scrollHeight;
            </script>
        """, height=420)


def process_llm_response(user_id, agent_id, user_message, language):
    """Process user message through LLM with conversation history and generate TTS audio"""
    try:
        # Check if Select AI is enabled
        use_select_ai = st.session_state.get("speech_use_select_ai", False)
        
        if use_select_ai:
            # Use Select AI service (similar to app_chat_01.py)
            profile_name = select_ai_service.get_profile(user_id)
            action = 'narrate'
            response_text = db_select_ai_service.get_chat(
                user_message,
                profile_name,
                action,
                language
            )
            
            # Handle "NNN" response (no information available)
            if "NNN" in response_text:
                response_text = st.session_state.get("language-message", "No tengo esa información.")
        else:
            # Use configured voice agent (original behavior)
            # Build context from recent conversation history
            context = ""
            recent_msgs = st.session_state.speech_conversation[-6:] if len(st.session_state.speech_conversation) > 6 else st.session_state.speech_conversation
            
            if recent_msgs:
                context = "Historial de conversación reciente:\n"
                for msg in recent_msgs:
                    role = "Usuario" if msg["role"] == "user" else "Asistente"
                    context += f"{role}: {msg['content']}\n"
                context += "\nConsidera el historial anterior para responder coherentemente.\n\n"
            
            # Build full input with context
            full_input = f"{context}Pregunta actual: {user_message}"
            
            # Use get_agent method (simpler, more reliable)
            result = generative_service.get_agent(
                user_id=user_id,
                agent_id=agent_id,
                input=full_input
            )
            
            response_text = result.get("answer", "Lo siento, no pude generar una respuesta.")
    except Exception as e:
        print(f"Error in LLM processing: {e}")
        response_text = f"Error al procesar: {str(e)}"
    
    # Generate TTS audio
    audio_base64 = None
    audio_bytes = text_to_speech(response_text)
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode()
    
    # Add assistant response to conversation
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.speech_conversation.append({
        "role": "assistant",
        "content": response_text,
        "timestamp": timestamp,
        "audio": audio_base64
    })
    
    # Set the timestamp as the ID to autoplay (unique identifier)
    st.session_state.speech_autoplay_id = timestamp


def process_transcription_results():
    """Process transcription results from the queue"""
    updated = False
    while not st.session_state.speech_result_queue.empty():
        msg_type, content = st.session_state.speech_result_queue.get()
        
        if msg_type == "final":
            # Add final transcription to conversation
            st.session_state.speech_conversation.append({
                "role": "user",
                "content": content,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            # Queue for LLM processing
            if not st.session_state.speech_processing_llm:
                st.session_state.speech_llm_queue.put(content)
            
            st.session_state.speech_current_partial = ""
            updated = True
        
        elif msg_type == "partial":
            st.session_state.speech_current_partial = content
            updated = True
        
        elif msg_type == "error":
            st.error(f"Error: {content}")
    
    return updated


def cleanup_session():
    """Cleanup OCI thread and queues when WebRTC stops"""
    if "speech_oci_thread" in st.session_state:
        if st.session_state.speech_oci_thread.is_alive():
            st.session_state.speech_audio_queue.put(None)
            st.session_state.speech_oci_thread.join(timeout=2.0)
        del st.session_state.speech_oci_thread
    
    # Clear queues
    while not st.session_state.speech_audio_queue.empty():
        st.session_state.speech_audio_queue.get()
    while not st.session_state.speech_result_queue.empty():
        st.session_state.speech_result_queue.get()


def create_oci_worker(audio_queue, result_queue, language):
    """Create OCI worker thread for real-time speech recognition"""
    def oci_worker(audio_q, result_q, lang):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async_input_queue = asyncio.Queue()
        
        def on_final(text):
            result_q.put(("final", text))
        
        def on_partial(text):
            result_q.put(("partial", text))
        
        async def bridge_audio():
            while True:
                if not audio_q.empty():
                    data = audio_q.get()
                    await async_input_queue.put(data)
                    if data is None:
                        break
                else:
                    await asyncio.sleep(0.01)
        
        bridge_task = loop.create_task(bridge_audio())
        try:
            loop.run_until_complete(
                start_realtime_session(on_final, on_partial, lang, async_input_queue)
            )
        except Exception as e:
            print(f"OCI Worker Error: {e}")
            result_q.put(("error", str(e)))
        finally:
            if not bridge_task.done():
                bridge_task.cancel()
            try:
                pending = asyncio.all_tasks(loop)
                loop.run_until_complete(asyncio.gather(*pending))
            except:
                pass
            loop.close()
    
    thread = threading.Thread(
        target=oci_worker,
        args=(audio_queue, result_queue, language),
        daemon=True
    )
    add_script_run_ctx(thread)
    thread.start()
    return thread


if login:
    st.set_page_config(
        page_title="Oracle AI Accelerator - Voice Chat",
        page_icon="🅾️",
        layout="centered"
    )
    
    # Header
    st.header(":material/mic: Voice Chat")
    st.caption("OCI Speech is an AI service for accurate speech-to-text transcription and text-to-speech synthesis, with timestamps, accessible from OCI Console, Data Science Notebooks, REST APIs, CLI, or SDK.")
    
    # Get user information
    username = st.session_state.get("username", "user")
    user_id = st.session_state.get("user_id", 1)
    language = st.session_state.get("language", "Spanish")
    
    # Initialize session state
    initialize_session_state()
    
    # Get configuration from sidebar (set in st_login.py)
    use_select_ai = st.session_state.get("speech_use_select_ai", False)
    selected_agent_id = st.session_state.get("speech_agent_id")
    selected_language = st.session_state.get("speech_language", language)
    
    # Validate agent is selected (only if Select AI is not enabled)
    if not use_select_ai and not selected_agent_id:
        st.info("Por favor, selecciona un agente en el menú lateral para comenzar.", icon=":material/settings:")
        st.stop()
    
    
    conversation_container = st.empty()
    status_caption = st.empty()
    
    # Render initial conversation
    render_conversation(conversation_container, st.session_state.speech_current_partial)
    
    # Clear autoplay flag after first render
    if st.session_state.speech_autoplay_id is not None:
        st.session_state.speech_autoplay_id = None
    
    # Process LLM queue (before WebRTC to avoid blocking)
    if not st.session_state.speech_llm_queue.empty() and not st.session_state.speech_processing_llm:
        st.session_state.speech_processing_llm = True
        st.rerun()
    
    if st.session_state.speech_processing_llm and not st.session_state.speech_llm_queue.empty():
        try:
            user_message = st.session_state.speech_llm_queue.get()
            # Pass language to process_llm_response
            process_llm_response(user_id, selected_agent_id, user_message, selected_language)
            # Update conversation display after processing
            render_conversation(conversation_container, st.session_state.speech_current_partial)
        except Exception as e:
            st.error(f"Error procesando mensaje: {e}")
        finally:
            st.session_state.speech_processing_llm = False
            st.rerun()
    
    # WebRTC Configuration
    RTC_CONFIGURATION = RTCConfiguration(RTC_ICE_SERVERS)
    
    ctx = webrtc_streamer(
        key=f"speech-chat-{st.session_state.speech_session_id}",
        mode=WebRtcMode.SENDONLY,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": False, "audio": True},
        audio_processor_factory=OCIAudioProcessor,
    )
    
    # Inject queue into audio processor
    if ctx.audio_processor:
        ctx.audio_processor.audio_queue = st.session_state.speech_audio_queue
    
    # Detect state transitions
    if st.session_state.speech_was_playing and not ctx.state.playing:
        cleanup_session()
        st.session_state.speech_session_id += 1
        st.session_state.speech_was_playing = False
    
    st.session_state.speech_was_playing = ctx.state.playing
    
    # Process while active
    if ctx.state.playing:
        status_caption.info("Listening...")
        
        # Ensure audio processor has queue
        if ctx.audio_processor and not ctx.audio_processor.audio_queue:
            ctx.audio_processor.audio_queue = st.session_state.speech_audio_queue
        
        # Start OCI thread if not exists
        if "speech_oci_thread" not in st.session_state or not st.session_state.speech_oci_thread.is_alive():
            st.session_state.speech_oci_thread = create_oci_worker(
                st.session_state.speech_audio_queue,
                st.session_state.speech_result_queue,
                selected_language
            )
        
        # Process transcriptions continuously
        loop_count = 0
        while ctx.state.playing and loop_count < MAX_PROCESSING_LOOPS:
            
            # Process all available messages in queue
            while not st.session_state.speech_result_queue.empty():
                msg_type, content = st.session_state.speech_result_queue.get()
                
                if msg_type == "final":
                    # Add final transcription to conversation
                    st.session_state.speech_conversation.append({
                        "role": "user",
                        "content": content,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })
                    
                    # Queue for LLM processing
                    if not st.session_state.speech_processing_llm:
                        st.session_state.speech_llm_queue.put(content)
                    
                    st.session_state.speech_current_partial = ""
                    # Force rerun to show new message
                    st.rerun()
                
                elif msg_type == "partial":
                    st.session_state.speech_current_partial = content
                    # Update only the partial text display without regenerating entire conversation
                
                elif msg_type == "error":
                    st.error(f"Error: {content}")
            
            time.sleep(LOOP_SLEEP_TIME)
            loop_count += 1
        
        # Force rerun if reached max loops and still playing
        if loop_count >= MAX_PROCESSING_LOOPS and ctx.state.playing:
            time.sleep(0.1)
            st.rerun()
    else:
        # Update status when not playing
        status_caption.caption("")
