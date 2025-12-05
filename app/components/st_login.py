import ast
import pandas as pd
import streamlit as st
import json
from datetime import datetime

import services.database as database

global_version = "2.0.2"

# Initialize the service
db_user_service = database.UserService()
db_agent_service = database.AgentService()

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
        st.page_link("pages/app_agents.py", label="Agents", icon=":material/smart_toy:")
        st.page_link("pages/app_agent_builder.py", label="Agent Builder", icon=":material/flowchart:")
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

        st.subheader("Options")
        
        if st.session_state["page"] == "app_chat_01.py":
            with st.container(border=True, key="options_select_ai_container"):
            
                # Widgets shared by all the pages
                user_id = st.session_state["user_id"]
                df_agents = db_agent_service.get_all_agents_cache(user_id, force_update=True)
                df_agents = df_agents[df_agents["AGENT_TYPE"] == "Analytics"]

                st.selectbox(
                    "Select an Agent",
                    options=df_agents["AGENT_ID"],
                    format_func=lambda agent_id: f"{agent_id}: {df_agents.loc[df_agents['AGENT_ID'] == agent_id, 'AGENT_NAME'].values[0]}",
                    key="selected_agent_id"
                )
                
                st.checkbox("Analytics Agent", False, key="analytics_agent")
                st.checkbox("SQLExplain Agent", False, key="sql_explain_agent")

                col1, col2, = st.columns(2)

                with col1:
                    if st.button(key="clear", help="Clear Chat", label="", icon=":material/delete:", disabled=(not st.session_state["chat-select-ai"]), use_container_width=True):
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
                        ], indent=4),
                        file_name=f"chat_history_{datetime.now().strftime('%H%M%S%f')}.json",
                        mime="text/plain",
                        disabled=(not st.session_state["chat-select-ai"]), 
                        use_container_width=True
                    )

        if st.session_state["page"] == "app_agent_builder.py":
            with st.container(border=True, key="options_agent_builder_container"):

                def queue_agent_builder_action(action_type: str):
                    st.session_state['agent_builder_pending_action'] = {
                        "type": action_type,
                        "timestamp": datetime.now().isoformat()
                    }
            
                if st.button("Add Tool", key="sidebar_add_tool", icon="🔶", use_container_width=True):
                    queue_agent_builder_action('TOOL')
                    st.rerun()
            
                if st.button("Add Task", key="sidebar_add_task", icon="🟢", use_container_width=True):
                    queue_agent_builder_action('TASK')
                    st.rerun()

            
                if st.button("Add Agent", key="sidebar_add_agent", icon="🟦", use_container_width=True):
                    queue_agent_builder_action('AGENT')
                    st.rerun()
            
                if st.button("Add Team", key="sidebar_add_team", icon="🔴", use_container_width=True):
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
                        use_container_width=True
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
                            use_container_width=True
                        )
                    else:
                        st.button(
                            key="save_speech_disabled",
                            label="",
                            help="Save Conversation",
                            icon=":material/download:",
                            disabled=True,
                            use_container_width=True
                        )

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