import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
import streamlit.components.v1 as components

import json
from pathlib import Path
from datetime import datetime
import asyncio
import requests
from PIL import Image
from io import BytesIO
import threading
import queue
import time

from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from services.oci_speech_stt_realtime import start_realtime_session, OCIAudioProcessor

import components as component
import services.database as database
import services as service
import utils as utils



language_map = {
    "Spanish"    : "esa",
    "Portuguese" : "ptb",
    "English"    : "gb"
}

map_state = {
    1: "Active",
    2: "Inactive",
    0: "Delete"
}
reverse_map_state = {v: k for k, v in map_state.items()}

st.set_page_config(
    page_title="Oracle AI Accelerator",
    page_icon="🅾️",
)

# Load login and footer components
st.session_state["page"] = "app.py"
login = component.get_login()
component.get_footer()

if login:
    # Session state init
    if "show_form_app" not in st.session_state:
        st.session_state["show_form_app"] = False
        st.session_state["form_mode_app"] = "create"
        st.session_state["selected_file"] = None

    if "username" in st.session_state and "user_id" in st.session_state:
        # Lazy init: servicios y conexiones solo después de login exitoso
        db_module_service             = database.ModuleService()
        db_agent_service              = database.AgentService()
        bucket_service                = service.BucketService()
        select_ai_service             = service.SelectAIService()
        select_ai_rag_service         = service.SelectAIRAGService()
        document_undestanding_service = service.DocumentUnderstandingService()
        speech_service                = service.SpeechService()
        document_multimodal           = service.DocumentMultimodalService()
        anomaly_engine_service        = service.AnalyzerEngineService()
        db_file_service               = database.FileService()
        db_doc_service                = database.DocService()
        utl_function_service          = utils.FunctionService()
        db_user_service               = database.UserService()
        st.header(":material/book_ribbon: Knowledge")
        st.caption("Manage Knowledge")
        st.set_page_config(layout="wide")
        st.set_page_config(initial_sidebar_state="expanded")
        
        st.session_state["page"] = "app.py"
        username = st.session_state["username"]
        user_id = st.session_state["user_id"]
        user_group_id = st.session_state["user_group_id"]
        language = st.session_state["language"]

        df_files = db_file_service.get_all_files(user_id)

        # Variables: Default
        file_src_strategy   = None
        trg_type            = None
        comment_data_editor = None

        # File List
        if not st.session_state["show_form_app"]:
            with st.container(border=True):
                st.badge("List Files")
                
                if df_files.empty:
                    st.info("No files found.")
                else:
                    df_view = df_files.copy()
                    df_view["Status"] = df_view["FILE_STATE"].map(map_state)
                    df_view["Select"] = False          

                    edited_df = st.data_editor(
                        df_view,
                        width="stretch",
                        hide_index=True,
                        num_rows="fixed",
                        key="data-files-list",
                        column_config={
                            "USER_ID"             : None,
                            "MODULE_ID"           : None,
                            "FILE_STATE"          : None,
                            "FILE_SRC_SIZE"       : None,
                            "FILE_SRC_STRATEGY"   : None,
                            "MODULE_VECTOR_STORE" : None,
                            "FILE_TRG_OBJ_NAME"   : None,
                            "FILE_TRG_TOT_PAGES"  : None,
                            "FILE_TRG_TOT_CHARACTERS" : None,
                            "FILE_TRG_TOT_TIME"   : None,
                            "FILE_TRG_LANGUAGE"   : None,
                            "FILE_TRG_PII"        : None,
                            "FILE_TRG_EXTRACTION" : None,
                            "OWNER"               : None,
                            "FILE_DESCRIPTION"    : None,
                            "USER_EMAIL"          : None,
                            "USER_GROUP_ID"       : None,
                            "USER_ID_OWNER"       : None,
                            "FILE_ID"             : st.column_config.Column("ID", disabled=True),
                            "MODULE_NAME"         : st.column_config.Column("Module", disabled=True),
                            "FILE_SRC_FILE_NAME"  : st.column_config.LinkColumn("Source File", display_text=r".*/(.+)$", disabled=True),
                            "FILE_TRG_OBJ_NAME"   : st.column_config.LinkColumn("Target File", display_text=r".*/(.+)$", disabled=True),
                            "USER_USERNAME"       : st.column_config.Column("Owner", disabled=True),
                            "FILE_USERS"          : st.column_config.Column("Share", disabled=True),
                            "FILE_DATE"           : st.column_config.Column("Change", disabled=True),
                            "FILE_VERSION"        : st.column_config.Column("Ver.", disabled=True),
                            "Status"              : st.column_config.Column("Status", disabled=True),
                            "Select"              : st.column_config.CheckboxColumn("Select", help="Select Record", default=False)
                        }
                    )

                    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([0.1, 0.1, 0.1, 0.7])
                    
                    if btn_col1.button(key="View", help="View", label="", type="secondary", width="stretch", icon=":material/table_eye:"):
                        rows_to_edit = edited_df[edited_df["Select"] == True]
                        if rows_to_edit.empty:
                            st.warning("Please select at least one file to view.", icon=":material/add_alert:")
                        else:
                            for _, selected_row in rows_to_edit.iterrows():
                                file_id = selected_row["FILE_ID"]
                                data = df_view[df_view["FILE_ID"] == file_id].iloc[0].to_dict()
                                st.session_state.update({
                                    "show_form_app": True,
                                    "form_mode_app": "view",
                                    "selected_file": data
                                })
                                st.rerun()

                    if btn_col2.button(key="Share", help="Share", label="", type="secondary", width="stretch", icon=":material/share:"):
                        rows = edited_df[edited_df["Select"] == True]

                        if rows.empty:
                            st.warning("Please select at least one file to share.", icon=":material/add_alert:")
                        else:
                            for _, selected_row in rows.iterrows():
                                module_id = selected_row["MODULE_ID"]
                                module_name = selected_row.get("MODULE_NAME", f"Module {module_id}")

                                # Validar si el módulo es no compartible
                                if module_id in [0, 1, 2]:
                                    st.warning(
                                        f"Cannot share file from **{module_name}**. Sharing is not allowed for these modules.",
                                        icon=":material/block:"
                                    )
                                    continue

                                # Validar si el usuario es el propietario del archivo
                                if selected_row["USER_ID"] != selected_row["USER_ID_OWNER"]:
                                    owner_email = selected_row.get("USER_EMAIL", "unknown@email.com")
                                    st.warning(
                                        f"Only the file owner can manage sharing. Please contact: **{owner_email}**",
                                        icon=":material/error:"
                                    )
                                    continue

                                # Abrir formulario de compartición
                                file_id = selected_row["FILE_ID"]
                                data = df_view[df_view["FILE_ID"] == file_id].iloc[0].to_dict()
                                st.session_state.update({
                                    "show_form_app": True,
                                    "form_mode_app": "share",
                                    "selected_file": data
                                })
                                st.rerun()

                    
                    if btn_col3.button(key="Delete", help="Delete", label="", type="secondary", width="stretch", icon=":material/delete:"):
                        try:
                            rows_to_edit = edited_df[edited_df["Select"] == True]
                            if rows_to_edit.empty:
                                st.warning("Please select at least one file to delete.", icon=":material/add_alert:")
                            else:
                                component.get_processing(True)

                                for _, row in rows_to_edit.iterrows():
                                    file_id = row["FILE_ID"]
                                    file_name = row["FILE_SRC_FILE_NAME"].rsplit("/", 1)[-1]
                                    object_name = row["FILE_SRC_FILE_NAME"].split("/o/")[-1]
                                    shared_users = row.get("FILE_USERS", 0)

                                    if row["OWNER"] == 1:
                                        if shared_users > 0:
                                            st.warning(
                                                f"File '{file_name}' cannot be deleted because it has been shared with {shared_users} user(s).",
                                                icon=":material/block:"
                                            )
                                            continue  # skip deletion
                                        # Eliminar completamente
                                        if bucket_service.delete_object(object_name):
                                            msg = db_file_service.delete_file(file_name, file_id)
                                            component.get_success(msg, icon=":material/database:")
                                    else:
                                        # Solo remover acceso
                                        msg = db_file_service.delete_file_user_by_user(file_id, user_id, file_name)
                                        component.get_success(msg, icon=":material/remove_circle:")

                                db_file_service.get_all_files.clear()
                                db_file_service.get_all_files(user_id)

                        except Exception as e:
                            component.get_error(f"[Error] Deleting File:\n{e}")
                        finally:
                            component.get_processing(False)

        # File View
        if st.session_state["show_form_app"]:
            mode = st.session_state["form_mode_app"]

            with st.container(border=True):
                st.badge(
                    "Create File" if mode == "create" else "View File" if mode == "view" else "Share File",
                    color="green" if mode == "create" else "blue" if mode == "view" else "orange"
                )
                data = st.session_state["selected_file"]

                if mode == "create":
                    df_modules = db_module_service.get_modules_cache(user_id, force_update=True)
                    df_agents = db_agent_service.get_all_agents_cache(user_id, force_update=True)
                    df_agents = df_agents[df_agents["AGENT_TYPE"] == "Extraction"]

                    if not df_modules.empty:
                        selected_module_id = st.selectbox(
                            "Which module would you like to start with?",
                            options=df_modules["MODULE_ID"],
                            format_func=lambda module_id: f"{module_id}: {df_modules.loc[df_modules['MODULE_ID'] == module_id, 'MODULE_NAME'].squeeze()}"
                        )

                        selected_agent_id = 0
                        if selected_module_id == 5 and not df_agents.empty:
                            selected_agent_id = st.selectbox(
                                "Which agent would you like to use?",
                                options=df_agents["AGENT_ID"],
                                format_func=lambda agent_id: f"{agent_id}: {df_agents.loc[df_agents['AGENT_ID'] == agent_id, 'AGENT_NAME'].values[0]} ({df_agents.loc[df_agents['AGENT_ID'] == agent_id, 'AGENT_TYPE'].values[0]})"
                            )

                        module_data = df_modules.loc[df_modules["MODULE_ID"] == selected_module_id].iloc[0]
                        selected_module_folder = module_data["MODULE_FOLDER"]
                        selected_src_types = utl_function_service.get_list_to_str(module_data["MODULE_SRC_TYPE"])
                        selected_trg_type = utl_function_service.get_list_to_str(module_data["MODULE_TRG_TYPE"])

                        selected_language_file = st.selectbox(
                            "What is the language of the file?",
                            options=list(language_map.keys()),
                            index=list(language_map.keys()).index(language)
                        )

                        selected_pii = False
                        if selected_module_id == 4:
                            selected_pii = st.radio(
                                "Enable detecting Personal Identifiable Information (PII)?",
                                options=[True, False],
                                index=1,
                                format_func=lambda x: "Yes" if x else "No",
                                horizontal=True
                            )

                        selected_uploaded = "File"
                        uploaded_files = None
                        uploaded_record = None

                        if selected_module_id == 4:
                            selected_uploaded = st.radio(
                                "What strategy do you want to upload?",
                                options=["File", "Record"],
                                horizontal=True
                            )
                            if selected_uploaded == "File":
                                uploaded_files = st.file_uploader(
                                    "Choose a File",
                                    type=selected_src_types,
                                    help="Limit 200MB",
                                    accept_multiple_files=True
                                )
                            elif selected_uploaded == "Record":
                                uploaded_record = st.audio_input("Record a voice message")

                        elif selected_module_id == 5:
                            uploaded_files = st.file_uploader(
                                "Choose a File",
                                type=selected_src_types,
                                help="Limit 200MB",
                                accept_multiple_files=True
                            )
                        
                        elif selected_module_id not in [5, 6]:
                            uploaded_files = st.file_uploader(
                                "Choose a File",
                                type=selected_src_types,
                                help="Limit 200MB",
                                accept_multiple_files=False
                            )

                        
                        uploaded_transcription = []
                        if selected_module_id == 6:
                            st.markdown("### Real-Time Transcription (WebRTC)")
                            
                            transcription_container = st.empty()
                            status_caption = st.empty()

                            # Path del JSON
                            output_dir = Path(f"files/{username}/module-ai-speech-to-realtime")
                            output_dir.mkdir(parents=True, exist_ok=True)
                            json_path = output_dir / "transcription.json"

                            # Cargar historial si no está en session state
                            if "transcriptions_list" not in st.session_state:
                                if json_path.exists() and json_path.stat().st_size > 0:
                                    with open(json_path, "r", encoding="utf-8") as f:
                                        st.session_state.transcriptions_list = json.load(f)
                                else:
                                    st.session_state.transcriptions_list = []
                            
                            # Sincronizar variable local para compatibilidad
                            uploaded_transcription = st.session_state.transcriptions_list

                            # Inicializar colas
                            if "webrtc_audio_queue" not in st.session_state:
                                st.session_state.webrtc_audio_queue = queue.Queue()
                            if "webrtc_result_queue" not in st.session_state:
                                st.session_state.webrtc_result_queue = queue.Queue()
                            
                            # Contador de sesiones WebRTC
                            if "webrtc_session_id" not in st.session_state:
                                st.session_state.webrtc_session_id = 0

                            # Función de renderizado
                            def render_transcriptions(partial_text=None):
                                transcription_html = ""
                                for item in st.session_state.transcriptions_list:
                                    transcription_html += f"""
                                        <div style="background-color:#21232B; padding:10px; border-radius:5px; margin-bottom:10px;">
                                            <div style="display:flex; justify-content:space-between;">
                                                <div style="width:35px; background-color:#E6A538; color:black; border-radius:5px; margin:2px; display:flex; align-items:center; justify-content:center;">
                                                    {item['id']}</div>
                                                <div style="width:100%; margin:2px; padding:5px;">{item['transcription']}</div>
                                            </div>
                                        </div>
                                    """
                                if partial_text:
                                    transcription_html += f"""
                                        <div style="background-color:#2A2A2A; padding:10px; border-radius:5px; margin-bottom:10px; opacity:0.6;">
                                            <div style="display:flex; justify-content:space-between;">
                                                <div style="width:35px; background-color:#AAAAAA; color:black; border-radius:5px; margin:2px; display:flex; align-items:center; justify-content:center;">
                                                    •••</div>
                                                <div style="width:100%; margin:2px; padding:5px;">{partial_text}</div>
                                            </div>
                                        </div>
                                    """
                                with transcription_container.container(border=True):
                                    st.markdown(":speech_balloon: :red[Real-Time] ***Customer Voice Transcription***")
                                    components.html(f"""
                                        <div id="scrollable-transcription" style="height:250px; overflow-y:auto; background-color:#1e1e1e; padding:10px; border-radius:10px; color:white; font-family:monospace;">
                                            {transcription_html}
                                        </div>
                                        <script>
                                            var div = window.parent.document.querySelectorAll('iframe[srcdoc]')[window.parent.document.querySelectorAll('iframe[srcdoc]').length - 1].contentWindow.document.getElementById('scrollable-transcription');
                                            if (div) div.scrollTop = div.scrollHeight;
                                        </script>
                                    """, height=270)

                            # Render inicial
                            render_transcriptions()

                            RTC_CONFIGURATION = RTCConfiguration(
                                {"iceServers": [
                                    {"urls": ["stun:stun.l.google.com:19302"]},
                                ]}
                            )

                            ctx = webrtc_streamer(
                                key=f"oci-speech-{st.session_state.webrtc_session_id}",
                                mode=WebRtcMode.SENDONLY,
                                rtc_configuration=RTC_CONFIGURATION,
                                media_stream_constraints={"video": False, "audio": True},
                                audio_processor_factory=OCIAudioProcessor,
                            )

                            # Inyectar la cola en el procesador una vez creado
                            if ctx.audio_processor:
                                ctx.audio_processor.audio_queue = st.session_state.webrtc_audio_queue
                            
                            # Detectar si acabamos de detener (transición de playing a stopped)
                            if "was_playing" not in st.session_state:
                                st.session_state.was_playing = False
                            
                            # Si estaba playing y ahora no lo está, acabamos de detener
                            if st.session_state.was_playing and not ctx.state.playing:
                                # Limpiar e incrementar contador para próxima sesión
                                if "oci_thread" in st.session_state:
                                    if st.session_state.oci_thread.is_alive():
                                        st.session_state.webrtc_audio_queue.put(None)
                                        st.session_state.oci_thread.join(timeout=2.0)
                                    del st.session_state.oci_thread
                                
                                # Limpiar colas
                                while not st.session_state.webrtc_audio_queue.empty():
                                    st.session_state.webrtc_audio_queue.get()
                                while not st.session_state.webrtc_result_queue.empty():
                                    st.session_state.webrtc_result_queue.get()
                                
                                # Incrementar para forzar nueva instancia en próximo Start
                                st.session_state.webrtc_session_id += 1
                                st.session_state.was_playing = False
                            
                            # Actualizar estado
                            st.session_state.was_playing = ctx.state.playing

                            if ctx.state.playing:
                                status_caption.info("Listening...")
                                
                                # Verificar si el procesador está recibiendo audio
                                if ctx.audio_processor and not ctx.audio_processor.audio_queue:
                                     ctx.audio_processor.audio_queue = st.session_state.webrtc_audio_queue
                                
                                if "oci_thread" not in st.session_state or not st.session_state.oci_thread.is_alive():
                                    # Capturar las colas y configuración ANTES de entrar al hilo
                                    audio_queue_ref = st.session_state.webrtc_audio_queue
                                    result_queue_ref = st.session_state.webrtc_result_queue
                                    
                                    # Pasamos el valor DIRECTO del selector (ej: "Spanish"), no el mapeado
                                    selected_lang_raw = selected_language_file 

                                    def oci_worker(audio_q, result_q, lang_raw):
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
                                            # Pasamos el idioma crudo ("Spanish") al servicio
                                            loop.run_until_complete(
                                                start_realtime_session(on_final, on_partial, lang_raw, async_input_queue)
                                            )
                                        except Exception as e:
                                            print(f"OCI Worker Error: {e}")
                                            result_q.put(("error", str(e)))
                                        finally:
                                            # Esperar a que el puente termine limpiamente si es posible
                                            if not bridge_task.done():
                                                bridge_task.cancel()
                                            # Ejecutar tareas pendientes de limpieza
                                            try:
                                                pending = asyncio.all_tasks(loop)
                                                loop.run_until_complete(asyncio.gather(*pending))
                                            except:
                                                pass
                                            loop.close()

                                    # Pasamos las referencias explícitamente al hilo
                                    t = threading.Thread(target=oci_worker, args=(audio_queue_ref, result_queue_ref, selected_lang_raw), daemon=True)
                                    add_script_run_ctx(t)
                                    t.start()
                                    st.session_state.oci_thread = t

                                partial_text = ""
                                while ctx.state.playing:
                                    updated = False
                                    # ... resto del loop ...
                                    while not st.session_state.webrtc_result_queue.empty():
                                        msg_type, content = st.session_state.webrtc_result_queue.get()
                                        
                                        if msg_type == "final":
                                            new_record = {
                                                "id": len(st.session_state.transcriptions_list) + 1,
                                                "transcription": content,
                                                "timestamp": datetime.now().isoformat()
                                            }
                                            st.session_state.transcriptions_list.append(new_record)
                                            uploaded_transcription = st.session_state.transcriptions_list
                                            
                                            with open(json_path, "w", encoding="utf-8") as f:
                                                json.dump(st.session_state.transcriptions_list, f, ensure_ascii=False)
                                            
                                            partial_text = ""
                                            updated = True
                                            
                                        elif msg_type == "partial":
                                            partial_text = content
                                            updated = True
                                            
                                        elif msg_type == "error":
                                            st.error(f"Error: {content}")

                                    if updated:
                                        render_transcriptions(partial_text)
                                    
                                    time.sleep(0.1)

                        file_description = st.text_area("File Description")                    

                        # ← CAMBIO: Preparar lista de items a procesar: uno(s) archivo(s) o la grabación
                        files_to_process = []
                        
                        if selected_module_id == 4:
                            if selected_uploaded == "File":
                                files_to_process = uploaded_files if isinstance(uploaded_files, list) else [uploaded_files]
                            elif selected_uploaded == "Record":
                                files_to_process = [uploaded_record] if uploaded_record else []  
                                            
                        elif selected_module_id == 6:
                            # Leer archivo JSON como entrada
                            if json_path.exists() and json_path.stat().st_size > 0:
                                with open(json_path, "r", encoding="utf-8") as f:
                                    files_to_process = [json.load(f)]

                        else:
                            files_to_process = uploaded_files if uploaded_files else []
                            if not isinstance(files_to_process, list):
                                files_to_process = [files_to_process]
                        
                        # Radio: Target Type
                        if selected_trg_type:
                            if len(selected_trg_type) == 1:
                                trg_type = selected_trg_type[0]
                            else:
                                trg_type = st.radio(
                                    "What would you1 like your target to be?",
                                    options=selected_trg_type,
                                    horizontal=True
                                )
                        else:
                            trg_type = None
                        
                        # ← CAMBIO: iteramos sobre cada archivo/grabación
                        for uploaded_file in files_to_process:

                            # Module: [6] Get file extension
                            if selected_module_id == 6:
                                file_extension = "json"
                            elif selected_uploaded == "Record":
                                file_extension = "wav"
                            elif selected_uploaded == "File" and uploaded_file:
                                file_extension = uploaded_file.name.rsplit(".", 1)[-1].lower()
                            else:
                                file_extension = ""
                            
                            # Module: [2] Select IA
                            if (file_extension == "csv") and (selected_module_id == 1):
                                with st.expander("Data Dictionary (Optional)"):
                                
                                    # Get column names for csv
                                    df_comment = utl_function_service.get_csv_column_comments(uploaded_file)
                                    
                                    # Data Editor: Comment
                                    comment_data_editor = st.data_editor(
                                        df_comment,
                                        width               = 'stretch',
                                        hide_index          = True,
                                        num_rows            = "fixed",
                                        column_config       = {
                                            "Column Name" : st.column_config.TextColumn(disabled=True),
                                            "Comment"     : st.column_config.TextColumn()
                                        }
                                    )
                    

                        warning_msg = None

                        # Validar entrada según módulo y estrategia
                        if selected_module_id == 6:
                            if not uploaded_transcription or len(uploaded_transcription) == 0:
                                warning_msg = "Please load a valid real-time transcription."

                        elif selected_uploaded == "File":
                            if not uploaded_files:
                                warning_msg = "Please upload at least one valid file."

                        elif selected_uploaded == "Record":
                            if not uploaded_record:
                                warning_msg = "Please record a message."

                        # Validar descripción solo si ya hay entrada válida
                        if not warning_msg and (not file_description or not file_description.strip()):
                            warning_msg = "Please enter a valid description."

                        # Mensaje final si hubo error
                        if warning_msg:
                            st.warning(warning_msg, icon=":material/add_alert:")


                        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([2, 2, 2, 4])

                        if btn_col1.button("Save", type="primary", width="stretch"):
                            
                            if warning_msg:
                                st.stop()
                            
                            try:
                                component.get_processing(True)
                                utl_function_service.track_time(1)

                                # ← CAMBIO: iteramos sobre cada archivo/grabación
                                for uploaded_file in files_to_process:

                                    # Variables
                                    module_id           = selected_module_id
                                    module_folder       = selected_module_folder
                                    now_str             = datetime.now().strftime('%H%M%S%f')
                                    file_name           = (uploaded_file.name if uploaded_file and hasattr(uploaded_file, "name") else f"rec_{now_str}.{file_extension or 'tmp'}")
                                    prefix              = f"{username}/{module_folder}"
                                    bucket_file_name    = (f"{prefix}/{file_name}").lower()
                                    bucket_file_content = (json.dumps(uploaded_file, ensure_ascii=False, indent=2).encode("utf-8")
                                                        if selected_module_id == 6 else uploaded_file.getvalue() if uploaded_file else uploaded_record)
                                    
                                    # Upload file to Bucket
                                    upload_file = bucket_service.upload_file(
                                        object_name     = bucket_file_name,
                                        put_object_body = bucket_file_content,
                                        msg             = True
                                    )                            

                                    if upload_file:
                                        # Set Variables
                                        file_src_file_name = utl_function_service.get_valid_url_path(file_name=bucket_file_name)
                                        file_src_size      = (json_path.stat().st_size if selected_module_id == 6 and json_path.exists()
                                                            else uploaded_file.size if uploaded_file and hasattr(uploaded_file, "size")
                                                            else uploaded_record.size if uploaded_record else 0)
                                        file_trg_obj_name  = (utl_function_service.get_valid_table_name(schema=f"SEL_AI_USER_ID_{user_id}", file_name=file_name)
                                                            if trg_type == "Autonomous Database"
                                                            else f"{file_src_file_name.rsplit('.', 1)[0]}_trg.{trg_type.lower()}")
                                        file_trg_language = language_map[selected_language_file]
                                        file_trg_pii      = 0
                                        file_description  = file_description
                                        # Insert File
                                        msg, file_id = db_file_service.insert_file(
                                            file_name,
                                            user_id,
                                            module_id,
                                            file_src_file_name,
                                            file_src_size,
                                            file_src_strategy,
                                            file_trg_obj_name,
                                            file_trg_language,
                                            file_trg_pii,
                                            file_description
                                        )
                                        component.get_toast(msg, icon=":material/database:")
                                        
                                        # Modules
                                        msg_module = None  # Inicializar msg_module por defecto
                                        match module_id:
                                            case 1:
                                                #msg = db_file_service.update_extraction(file_id, str(bucket_file_content))
                                                #component.get_toast(msg, ":material/database:")
                            
                                                msg_module = select_ai_service.create(
                                                    user_id,
                                                    file_src_file_name, 
                                                    file_trg_obj_name,
                                                    comment_data_editor
                                                )
                                                file_trg_obj_name       = file_trg_obj_name
                                                file_trg_tot_pages      = 1
                                                file_trg_tot_characters = len(bucket_file_content)
                                                file_trg_tot_time       = utl_function_service.track_time(0)
                                                file_trg_language       = language_map[selected_language_file]
                                            case 2:
                                                msg = db_file_service.update_extraction(file_id, str(bucket_file_content))
                                                component.get_toast(msg, ":material/database:")
                                                
                                                msg_module = select_ai_rag_service.create_profile(
                                                    user_id,
                                                    file_src_file_name
                                                )
                                                file_trg_obj_name       = select_ai_rag_service.get_index_name(user_id)
                                                file_trg_tot_pages      = 1
                                                file_trg_tot_characters = len(bucket_file_content)
                                                file_trg_tot_time       = utl_function_service.track_time(0)
                                                file_trg_language       = language_map[selected_language_file]
                                            case 3:
                                                object_name = bucket_file_name
                                                msg_module, data = document_undestanding_service.create(
                                                    object_name,
                                                    prefix,
                                                    language,
                                                    file_id
                                                )
                                                file_trg_obj_name       = file_trg_obj_name
                                                file_trg_tot_pages      = data[-1].get('page_number', 0) if data else 0
                                                file_trg_tot_characters = sum(page.get('characters', 0) for page in data) if data else 0
                                                file_trg_tot_time       = utl_function_service.track_time(0)
                                                file_trg_language       = language_map[selected_language_file]
                                            case 4:
                                                object_name = bucket_file_name
                                                msg_module, data = speech_service.create_job(
                                                    object_name,
                                                    prefix,
                                                    language,
                                                    file_id,
                                                    trg_type
                                                )
                                                file_trg_obj_name       = file_trg_obj_name
                                                file_trg_tot_pages      = 1
                                                file_trg_tot_characters = len(str(data))
                                                file_trg_tot_time       = utl_function_service.track_time(0)
                                                file_trg_language       = language_map[selected_language_file]
                                            case 5:
                                                object_name = bucket_file_name
                                                strategy    = "Single"
                                                agent_id    = selected_agent_id
                                                msg_module, data = document_multimodal.create(
                                                    object_name,
                                                    strategy,
                                                    user_id,
                                                    agent_id,
                                                    file_id,
                                                    username,
                                                    trg_type
                                                )
                                                file_trg_obj_name       = file_trg_obj_name
                                                file_trg_tot_pages      = 1
                                                file_trg_tot_characters = len(str(data))
                                                file_trg_tot_time       = utl_function_service.track_time(0)
                                                file_trg_language       = language_map[selected_language_file]
                                            case 6:
                                                object_name = bucket_file_name
                                                msg_module, data = speech_service.create(
                                                    object_name,
                                                    prefix,
                                                    language,
                                                    file_id,
                                                    trg_type
                                                )
                                                file_trg_obj_name       = file_trg_obj_name
                                                file_trg_tot_pages      = 1
                                                file_trg_tot_characters = len(str(data))
                                                file_trg_tot_time       = utl_function_service.track_time(0)
                                                file_trg_language       = language_map[selected_language_file]
                                                
                                                # Real-Time Transcription
                                                service.stop_realtime_session()
                                                uploaded_transcription.clear()
                                                with open(json_path, "w", encoding="utf-8") as f:
                                                    json.dump([], f)
                                                render_transcriptions()
                                                status_caption.caption("")
                                            case 7:
                                                object_name = bucket_file_name
                                                msg_module  = "Object retrieved successfully."
                                                data        = bucket_service.get_object(object_name).decode("utf-8")

                                                # Process file extraction
                                                msg = db_file_service.update_extraction(file_id, data)
                                                component.get_toast(msg, ":material/database:")

                                                # Process Vector Store
                                                msg = db_doc_service.vector_store(file_id)
                                                component.get_toast(msg, ":material/database:")

                                                file_trg_obj_name       = file_trg_obj_name
                                                file_trg_tot_pages      = 1
                                                file_trg_tot_characters = len(data)
                                                file_trg_tot_time       = utl_function_service.track_time(0)
                                                file_trg_language       = language_map[selected_language_file]
                                            case _:
                                                msg_module = f"Module {module_id} not implemented or invalid."

                                        # Update Extraction
                                        file_trg_tot_time = utl_function_service.track_time(0)
                                        db_file_service.update_file(
                                            file_id,
                                            file_trg_obj_name,
                                            file_trg_tot_pages,
                                            file_trg_tot_characters,
                                            file_trg_tot_time,
                                            file_trg_language
                                        )

                                        # PII
                                        if selected_pii:
                                            # Set Variables
                                            file_trg_obj_name   = f"{file_src_file_name.rsplit('.', 1)[0]}_trg_pii.{trg_type.lower()}"
                                            file_trg_pii        = (1 if selected_pii else 0)

                                            # Insert File
                                            msg, file_id = db_file_service.insert_file(
                                                file_name,
                                                user_id,
                                                module_id,
                                                file_src_file_name,
                                                file_src_size,
                                                file_src_strategy,
                                                file_trg_obj_name,
                                                file_trg_language,
                                                file_trg_pii,
                                                file_description
                                            )
                                            component.get_toast(msg, icon=":material/database:")

                                            object_name = bucket_file_name
                                            msg_module, data = anomaly_engine_service.create(
                                                object_name,
                                                language,
                                                file_id,
                                                data,
                                                trg_type
                                            )
                                            file_trg_obj_name       = file_trg_obj_name
                                            file_trg_tot_pages      = 1
                                            file_trg_tot_characters = len(str(data))
                                            file_trg_tot_time       = utl_function_service.track_time(0)
                                            file_trg_language       = language_map[selected_language_file]

                                            # Update Extraction
                                            file_trg_tot_time = utl_function_service.track_time(0)
                                            db_file_service.update_file(
                                                file_id,
                                                file_trg_obj_name,
                                                file_trg_tot_pages,
                                                file_trg_tot_characters,
                                                file_trg_tot_time,
                                                file_trg_language
                                            )

                                        db_module_service.get_modules_files_cache(user_id, force_update=True)
                                        db_file_service.get_all_files.clear()
                                        db_file_service.get_all_files(user_id)

                                        if msg_module:
                                            component.get_success(msg_module)

                                st.session_state["show_form_app"] = False
                                st.rerun()

                            except Exception as e:
                                component.get_error(f"[Error] Uploading File:\n{e}")
                            finally:
                                component.get_processing(False)

                        # Botón Cancel
                        if btn_col2.button("Cancel", width="stretch"):
                            st.session_state["show_form_app"] = False
                            st.rerun()

                        # Botón Clear para transcripciones en tiempo real (módulo 6)
                        if selected_module_id == 6:
                            if btn_col3.button("Clear", type="secondary", width="stretch", key="clear_transcriptions_btn"):
                                st.session_state.transcriptions_list = []
                                json_path_clear = Path(f"files/{username}/module-ai-speech-to-realtime") / "transcription.json"
                                if json_path_clear.exists():
                                    with open(json_path_clear, "w", encoding="utf-8") as f:
                                        json.dump([], f)
                                st.rerun()
                        else:
                            # Placeholder vacío para mantener el layout cuando no es módulo 6
                            btn_col3.empty()

                    else:
                        st.warning("No modules found for this user.", icon=":material/warning:")

                elif mode == "view":
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_input("ID", value=data["FILE_ID"], disabled=True)
                        st.text_input("Size", value=str(data["FILE_SRC_SIZE"]), disabled=True)
                        st.text_input("NLS", value=data["FILE_TRG_LANGUAGE"], disabled=True)
                        st.text_input("Pages", value=str(data["FILE_TRG_TOT_PAGES"]), disabled=True)
                        st.text_input("Time", value=str(data["FILE_TRG_TOT_TIME"]), disabled=True)
                        st.text_input("Owner", value=str(data["USER_USERNAME"]), disabled=True)
                        st.text_input("Ver.", value=data["FILE_VERSION"], disabled=True)

                    with col2:
                        st.text_input("Module", value=data["MODULE_NAME"], disabled=True)
                        st.text_input("Strategy", value=data["FILE_SRC_STRATEGY"], disabled=True)
                        st.text_input("PII", value=data["FILE_TRG_PII"], disabled=True)
                        st.text_input("Chars.", value=str(data["FILE_TRG_TOT_CHARACTERS"]), disabled=True)
                        st.text_input("Change", value=data["FILE_DATE"], disabled=True)
                        st.text_input("Owner Email", value=str(data["USER_EMAIL"]), disabled=True)
                        st.text_input("Status", value=data["Status"], disabled=True)
                        
                    st.text_input("Input", value=data["FILE_SRC_FILE_NAME"], disabled=True)
                    st.text_input("Output", value=data["FILE_TRG_OBJ_NAME"], disabled=True)
                    st.text_input("Description", value=data["FILE_DESCRIPTION"], disabled=True)

                    # Mostrar texto + imagen en columnas solo si el módulo es 5
                    if data["MODULE_ID"] == 5:
                        col_image, col_text = st.columns([0.4, 0.6])

                        with col_image:
                            try:
                                response = requests.get(data["FILE_SRC_FILE_NAME"], timeout=10)
                                if response.status_code == 200:
                                    st.image(Image.open(BytesIO(response.content)))
                            except Exception as e:
                                st.error(f"Error cargando imagen: {e}")
                        with col_text:
                            st.text_area("Text", value=data["FILE_TRG_EXTRACTION"], disabled=True, height=840)
                        

                    else:
                        st.text_area("Text", value=data["FILE_TRG_EXTRACTION"], disabled=True, height=500)

                    btn_col1, btn_col2 = st.columns([2.2, 8])

                    if btn_col1.button("Cancel", width="stretch"):
                        st.session_state["show_form_app"] = False
                        st.rerun()

                elif mode == "share":
                    file_id = data["FILE_ID"]

                    # Usuarios ya compartidos para este archivo
                    df = db_file_service.get_all_file_user_cache(user_id, force_update=True)
                    
                    # Obtener el grupo del usuario actual
                    is_admin = data["USER_GROUP_ID"] == 0  

                    # Cargar usuarios disponibles
                    if is_admin:
                        df_users = db_user_service.get_all_users_cache(force_update=True)
                        st.caption("You are sharing as **Administrator**. All users are available.")
                        row_users = df[df["FILE_ID"] == file_id]["USER_ID"].tolist()
                    else:
                        df_users = db_user_service.get_all_user_group_shared_cache(user_id, force_update=True)
                        row_users = df[(df["FILE_ID"] == file_id) & (df["USER_GROUP_ID"] == user_group_id)]["USER_ID"].tolist()
                    
                    # Si no hay usuarios disponibles, mostrar mensaje
                    if df_users.empty:
                        st.warning("There are no users available to share this file with.", icon=":material/person_off:")
                    else:
                        old_users = row_users

                        selected_user_ids = st.pills(
                            "Select Users to Share With",
                            options=df_users["USER_ID"],
                            format_func=lambda uid: f"{uid}: {df_users.loc[df_users['USER_ID'] == uid, 'USER_USERNAME'].values[0]}",
                            selection_mode="multi",
                            default=old_users,
                            disabled=df_users.empty
                        )

                        new_users = selected_user_ids

                    btn_col1, btn_col2, _ = st.columns([2, 2.2, 5.8])

                    if btn_col1.button("Save", type="primary", width="stretch", disabled=df_users.empty):
                        try:
                            if set(old_users) != set(new_users):
                                component.get_processing(True)
                                msg = db_file_service.update_file_user(file_id, new_users)
                                component.get_success(msg, icon=":material/update:")
                                db_file_service.get_all_file_user_cache(user_id, force_update=True)
                                db_file_service.get_all_files.clear()
                                db_file_service.get_all_files(user_id)
                                st.session_state["show_form_app"] = False
                                st.rerun()
                            else:
                                st.warning("No changes detected.")
                        except Exception as e:
                            component.get_error(f"[Error] Updating shared users:\n{e}")
                        finally:
                            component.get_processing(False)

                    if btn_col2.button("Cancel", width="stretch"):
                        st.session_state["show_form_app"] = False
                        st.rerun()

        # Toggle form state
        if not st.session_state["show_form_app"]:
            btn_col1, btn_col2 = st.columns([2, 8])

            if btn_col1.button("Create", type="primary", width="stretch"):
                st.session_state["show_form_app"] = True
                st.session_state["form_mode_app"] = "create"
                st.session_state["selected_file"] = None
                st.rerun()


# Run the application (Windows)
# .venv/Scripts/Activate.ps1
# cd .\app\
# streamlit run .\app.py --server.port 8501

# Show the last 200 lines of the log file (Oracle Linux)
# tail -n 200 /home/opc/streamlit.log

# Kill the process running on port 8501 (Oracle Linux)
# sudo lsof -t -i:8501 | xargs sudo kill -9

# Run the application (Oracle Linux)
# cd /home/opc/oracle-ai-accelerator/app
# echo "Using Python from: $(which python)"
# nohup python -m streamlit run app.py --server.port 8501 --logger.level=INFO > /home/opc/streamlit.log 2>&1 &