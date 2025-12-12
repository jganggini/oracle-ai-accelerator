import ast
import pandas as pd
import streamlit as st
import json
import time
import random
from datetime import datetime

import services.database as database

global_version = "2.0.4"

# Initialize the service
db_user_service = database.UserService()
db_agent_service = database.AgentService()
db_quiz_service = database.QuizService()
db_file_service = database.FileService()

def parse_modules(modules):
    """
    Parse modules from a JSON-like string or a comma-separated string.

    Args:
        modules (str): A string representing modules in JSON or comma-separated format.

    Returns:
        list: A list of module names.
    """
    try:
        # Handle Python-style string list
        return ast.literal_eval(modules)
    except (ValueError, SyntaxError):
        # Fallback to comma-separated format
        return [m.strip().strip('"') for m in modules.strip('[]').split(',')]

def get_menu(modules, user):
    """
    Build and display the sidebar menu based on the user's modules.

    Args:
        modules (str): The user's accessible modules.
        user (str): The user's name to display in the sidebar.
    """
    module_list = parse_modules(modules)  # Parse the module list correctly
    
    with st.sidebar:
        st.image("images/st_pages.gif")        

        st.markdown("## :red[Oracle AI] Accelerator :gray-badge[:material/smart_toy: " + global_version + "]")
        
        st.write(f"Hi, **:blue-background[{user}]**")

        # Always shown links
        st.page_link("app.py", label="Knowledge", icon=":material/book_ribbon:")
        
        # Agents solo si tiene módulos con vector store
        if "Vector Database" in st.session_state.get("modules", ""):
            st.page_link("pages/app_agents.py", label="Agents", icon=":material/smart_toy:")
            st.page_link("pages/app_agent_builder.py", label="Agent Builder", icon=":material/flowchart:")
        
        # Quiz solo si tiene el módulo 8
        if "Quiz" in st.session_state.get("modules", ""):
            st.page_link("pages/app_quiz.py", label="Quiz", icon=":material/quiz:")
        #st.page_link("pages/app_speech.py", label="Voice Chat", icon=":material/mic:")

        # AI Demos Section
        ai_demos = [
            ("AI Speech Real-Time", "pages/app_speech.py", ":material/mic:"),
            ("Select AI", "pages/app_chat_01.py", ":material/smart_toy:"),
            ("Select AI RAG", "pages/app_chat_02.py", ":material/plagiarism:"),
            ("Vector Database", "pages/app_chat_03.py", ":material/network_intelligence:")
        ]
        available_demos = [demo for demo in ai_demos if demo[0] in module_list]

        if available_demos:
            for label, page, icon in available_demos:
                st.page_link(page, label=label, icon=icon)
        
        # Settings Section
        st.subheader("Settings")
        if "Administrator" in module_list:
            st.page_link("pages/app_users.py", label="Users", icon=":material/settings_account_box:")
            st.page_link("pages/app_user_group.py", label="User Group", icon=":material/group:")
        st.page_link("pages/app_profile.py", label="Profile", icon=":material/manage_accounts:")
        
        # Reports Section (only for Administrators)
        if "Administrator" in module_list:
            st.subheader("Reports")
            st.page_link("pages/app_quiz_report.py", label="Quiz Reports", icon=":material/analytics:")
        
        st.subheader("Options")
        
        
        if st.session_state["page"] == "app_chat_01.py":
            with st.container(border=True, key="options_select_ai_container"):
            
                # Widgets shared by all the pages
                user_id = st.session_state["user_id"]
                df_agents = db_agent_service.get_all_agents_cache(user_id, force_update=True)
                df_agents = df_agents[df_agents["AGENT_TYPE"] == "Analytics"]

                # Modo de acción para Select AI (narrate/showsql/explainsql)
                action_options = ["narrate", "showsql", "explainsql", "runsql", "chat"]
                st.selectbox(
                    "Select AI Action",
                    options=action_options,
                    index=action_options.index(st.session_state.get("select_ai_action", "narrate"))
                    if st.session_state.get("select_ai_action", "narrate") in action_options
                    else 0,
                    key="select_ai_action"
                )
                
                st.checkbox("Analytics Agent", False, key="analytics_agent")
                # Deshabilitamos el uso del Explain Agent; mantener la clave en False evita regresiones
                st.session_state["sql_explain_agent"] = False

                # Selección de agente visible solo cuando Analytics Agent está activo
                analytics_enabled = st.session_state.get("analytics_agent", False)
                if analytics_enabled and not df_agents.empty:
                    st.selectbox(
                        "Select an Agent",
                        options=df_agents["AGENT_ID"],
                        format_func=lambda agent_id: f"{agent_id}: {df_agents.loc[df_agents['AGENT_ID'] == agent_id, 'AGENT_NAME'].values[0]}",
                        index=0,
                        key="selected_agent_id"
                    )
                elif not analytics_enabled:
                    # Evitamos estados inconsistentes cuando se desactiva el modo Analytics
                    st.session_state["selected_agent_id"] = st.session_state.get("selected_agent_id")

                col1, col2, = st.columns(2)

                with col1:
                    if st.button(key="clear", help="Clear Chat", label="", icon=":material/delete:", disabled=(not st.session_state["chat-select-ai"]), width="stretch"):
                        st.session_state["chat-select-ai"] = []
                        st.rerun()

                with col2:
                    st.download_button(
                        key="Save",
                        label="",
                        help="Save Chat",
                        icon=":material/download:",
                        data=json.dumps([
                            {k: v for k, v in msg.items() if k not in ("analytics_df", "analytics")}
                            for msg in st.session_state["chat-select-ai"]
                        ], indent=4, ensure_ascii=False),
                        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        disabled=(not st.session_state["chat-select-ai"]), 
                        width="stretch"
                    )

        if st.session_state["page"] == "app_agent_builder.py":
            with st.container(border=True, key="options_agent_builder_container"):

                def queue_agent_builder_action(action_type: str):
                    st.session_state['agent_builder_pending_action'] = {
                        "type": action_type,
                        "timestamp": datetime.now().isoformat()
                    }
            
                if st.button("Add Tool", key="sidebar_add_tool", icon="🔶", width="stretch"):
                    queue_agent_builder_action('TOOL')
                    st.rerun()
            
                if st.button("Add Task", key="sidebar_add_task", icon="🟢", width="stretch"):
                    queue_agent_builder_action('TASK')
                    st.rerun()

            
                if st.button("Add Agent", key="sidebar_add_agent", icon="🟦", width="stretch"):
                    queue_agent_builder_action('AGENT')
                    st.rerun()
            
                if st.button("Add Team", key="sidebar_add_team", icon="🔴", width="stretch"):
                    queue_agent_builder_action('TEAM')
                    st.rerun()
        
        if st.session_state["page"] == "app_speech.py":
            with st.container(border=True, key="options_speech_container"):
                
                # Get user agents for voice chat
                user_id = st.session_state["user_id"]
                df_agents = db_agent_service.get_all_agents_cache(user_id, force_update=False)
                df_agents = df_agents[df_agents["AGENT_TYPE"] == "Voice"]
                
                if not df_agents.empty:
                    # Disable agent selection if Select AI is enabled
                    use_select_ai = st.session_state.get("speech_use_select_ai", False)
                    st.selectbox(
                        "Select an Agent",
                        options=df_agents["AGENT_ID"],
                        format_func=lambda agent_id: f"{agent_id}: {df_agents.loc[df_agents['AGENT_ID'] == agent_id, 'AGENT_NAME'].values[0]}",
                        key="speech_agent_id",
                        disabled=use_select_ai
                    )
                
                # Language selector
                language_options = ["Spanish", "Portuguese", "English"]
                current_language = st.session_state.get("language", "Spanish")
                default_index = language_options.index(current_language) if current_language in language_options else 0
                
                st.selectbox(
                    "Language",
                    options=language_options,
                    index=default_index,
                    key="speech_language"
                )
                
                # Select AI checkbox
                st.checkbox(
                    "Select AI",
                    value=st.session_state.get("speech_use_select_ai", False),
                    key="speech_use_select_ai",
                    help="Use Select AI to answer queries based on database tables instead of the configured voice agent"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(
                        key="clear_speech",
                        help="Clear Conversation",
                        label="",
                        icon=":material/delete:",
                        disabled=(not st.session_state.get("speech_conversation", [])),
                        width="stretch"
                    ):
                        st.session_state["speech_conversation"] = []
                        st.session_state["speech_current_partial"] = ""
                        st.session_state["speech_processing_llm"] = False
                        st.rerun()
                
                with col2:
                    if st.session_state.get("speech_conversation", []):
                        history_json = json.dumps(
                            st.session_state["speech_conversation"],
                            indent=4,
                            ensure_ascii=False
                        )
                        st.download_button(
                            key="save_speech",
                            label="",
                            help="Save Conversation",
                            icon=":material/download:",
                            data=history_json,
                            file_name=f"voice_chat_{datetime.now().strftime('%H%M%S%f')}.json",
                            mime="application/json",
                            width="stretch"
                        )
                    else:
                        st.button(
                            key="save_speech_disabled",
                            label="",
                            help="Save Conversation",
                            icon=":material/download:",
                            disabled=True,
                            width="stretch"
                        )
        
        if st.session_state["page"] == "app_quiz.py":
            with st.container(border=True, key="options_quiz_container"):
                user_id = st.session_state.get("user_id")
                df_files = db_file_service.get_all_files(user_id) if user_id else None
                df_quiz_files = df_files[df_files["MODULE_ID"] == 8] if df_files is not None and not df_files.empty else None
                
                if df_quiz_files is None or df_quiz_files.empty:
                    st.info("No quizzes available. Please contact the administrator.", icon=":material/info:")
                else:
                    quiz_running = st.session_state.get("quiz_started", False) and not st.session_state.get("quiz_finished", False)
                    quiz_finished = st.session_state.get("quiz_finished", False)
                    
                    # Show selector only when quiz is not running/finished
                    if not quiz_running and not quiz_finished:
                        selected_file_id = st.selectbox(
                            "Select Quiz",
                            options=df_quiz_files["FILE_ID"].tolist(),
                            format_func=lambda fid: f"{df_quiz_files.loc[df_quiz_files['FILE_ID'] == fid, 'FILE_DESCRIPTION'].values[0]}",
                            key="quiz_selected_file_id"
                        )
                        df_all_questions_sidebar = db_quiz_service.get_quiz_questions(selected_file_id)
                        st.caption(f"Total available questions: **{len(df_all_questions_sidebar)}**")
                    
                    # Quiz in progress - show info and Leave button
                    elif quiz_running:
                        st.markdown("**Evaluation in Progress**")
                        
                        # Evaluation name
                        st.caption(f"{st.session_state.get('quiz_evaluation_name', '')}")
                        
                        # Timer
                        if st.session_state.get("quiz_start_time"):
                            elapsed = int(time.time() - st.session_state["quiz_start_time"])
                            st.metric(
                                "Elapsed Time",
                                f"{elapsed // 60}:{elapsed % 60:02d}",
                                delta=None
                            )
                        
                        # Leave Quiz button
                        if st.button("Leave Quiz", type="secondary", icon=":material/cancel:", width="stretch"):
                            if st.session_state.get("quiz_confirm_abandon", False):
                                st.session_state["quiz_started"] = False
                                st.session_state["quiz_finished"] = False
                                st.session_state["quiz_confirm_abandon"] = False
                                st.rerun()
                            else:
                                st.session_state["quiz_confirm_abandon"] = True
                                st.warning("Click again to confirm")
                    
                    # Quiz finished - show score and reset button
                    elif quiz_finished:
                        answers = st.session_state.get("quiz_answers", {})
                        if answers:
                            correct = sum(1 for ans in answers.values() if ans["is_correct"] == 1)
                            total = len(answers)
                            st.metric("Score", f"{(correct/total)*100:.1f}%")
                        
                        # Take Another Quiz button
                        if st.button("Take Quiz", type="primary", icon=":material/refresh:", width="stretch"):
                            # Clear all quiz-related keys
                            for key in list(st.session_state.keys()):
                                if key.startswith("quiz_") or key.startswith("saved_option_"):
                                    del st.session_state[key]
                            st.rerun()

        # Sign out button
        if st.button(":material/exit_to_app: Sign out", type="secondary"):
            st.set_page_config(layout="centered")
            st.set_page_config(initial_sidebar_state="collapsed")
            st.cache_data.clear()
            st.cache_resource.clear()
            st.session_state.clear()
            st.rerun()

def get_login():
    """
    Handle the login process and render the appropriate menu.
    """
    if all(k in st.session_state for k in ["username", "user", "user_id", "modules", "chat-history", "chat-save"]):
        get_menu(st.session_state["modules"], st.session_state["user"])
        return True
    else:
        # Login Form
        with st.form('form-login'):

            st.markdown("## :red[Oracle AI] Accelerator :gray-badge[:material/smart_toy: " + global_version + "]")

            col1, col2 = st.columns(2)
            with col1:
                st.image("images/st_login.gif")
                st.markdown(
                    ":gray-badge[:material/smart_toy: Agents] "
                    ":gray-badge[:material/database: Autonomous 26ai] "
                    ":gray-badge[:material/database_search: Select AI] "
                    ":gray-badge[:material/plagiarism: Select AI RAG] "
                    ":gray-badge[:material/psychology: Generative AI] "
                    ":gray-badge[:material/privacy_tip: PII Detection] "
                    ":gray-badge[:material/flowchart: Agent Builder] "
                    ":gray-badge[:material/mic: AI Speech STT/TTS RealTime] "
                    ":gray-badge[:material/description: Document Understanding] "
                )
            with col2:                
                username = st.text_input('Username')
                password = st.text_input('Password', type='password')
                # Selectbox: Laguage
                language = st.selectbox(
                    "Language",
                    options=("Spanish", "Portuguese", "English")
                )
                language_message = None
                match language:
                    case "Spanish":
                        language_message = "No tengo esa información."
                    case "Portuguese":
                        language_message = "Não tenho essa informação."
                    case "English":
                        language_message = "I don't have that information."

                btn_login = st.form_submit_button('Login', type='primary')

            if btn_login:
                df = db_user_service.get_access(username, password)

                if df is not None and not df.empty:
                    user_state = df['USER_STATE'].iloc[0]

                    # Check if user is deactivate
                    if user_state == 1:
                        # Set session state
                        st.session_state.update({
                            'page'               : "app.py",
                            'user_id'            : int(df['USER_ID'].iloc[0]),
                            'user_group_id'      : int(df['USER_GROUP_ID'].iloc[0]),
                            'modules'            : df['MODULE_NAMES'].iloc[0],
                            'username'           : df['USER_USERNAME'].iloc[0],
                            'user'               : f"{df['USER_NAME'].iloc[0]}, {df['USER_LAST_NAME'].iloc[0]}",
                            'language'           : language,
                            'language-message'   : language_message,
                            'chat-select-ai'     : [],
                            'chat-select-ai-rag' : [],
                            'chat-docs'          : [],
                            'chat-save'          : [],
                            'chat-modules'       : [],
                            'chat-objects'       : [],
                            'chat-agent'         : 0,
                            'chat-history'       : [],
                            'ai-agent'           : None
                        })
                        st.switch_page("app.py")
                    
                    else:
                        st.error("This user is deactivated.", icon=":material/gpp_maybe:")
                
                else:
                    st.error("Invalid username or password", icon=":material/gpp_maybe:")
        
        return False