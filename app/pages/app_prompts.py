import time
import base64
import json
from datetime import datetime
import streamlit as st
from streamlit_float import *

from annotated_text import annotated_text, annotation
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

import components as component
import services.database as database
import services as service
import utils as utils

# Initialize services
db_module_service = database.ModuleService()
db_agent_service = database.AgentService()
db_user_service = database.UserService()
db_prompt_service = database.PromptService()

if "show_form_prompts" not in st.session_state:
    st.session_state["show_form_prompts"] = False

st.set_page_config(
    page_title="Oracle AI Accelerator: Prompts",
    page_icon="🅾️",
)

login = component.get_login()
component.get_footer()

if login:
    st.header(":material/smart_toy: Prompts")
    st.caption("Manage prompts for model.")

    user_id = st.session_state["user_id"]
    user_group_id = st.session_state["user_group_id"]
    df_prompts = db_prompt_service.get_all_prompts_cache(user_id, force_update=True)
    df_users = db_user_service.get_all_users_cache()

    if not st.session_state["show_form_prompts"]:
        with st.container(border=True):
            st.badge("List Prompts")

            if df_prompts.empty:
                st.info("No prompts found.")
            else:
                df_view = df_prompts.copy()
                df_view["Select"] = False
                
                edited_df = st.data_editor(
                    df_view,
                    use_container_width=True,
                    hide_index=True,
                    num_rows="fixed",
                    key="data-prompt-list"
                )

    btn_col1, btn_col2 = st.columns([2, 8])
            
    if btn_col1.button("Create", type="primary", use_container_width=True):
        if not st.session_state["show_form_prompts"]:
            st.session_state["show_form_prompts"] = "create"
        else:
            st.session_state["show_form_prompts"] = False


    if st.session_state["show_form_prompts"]:
        mode = st.session_state["show_form_prompts"]

        with st.container(border=True):
            st.badge(
                "Create Prompt",
                color="green"
            )

            if mode == "create" or mode == "edit":
                prompt_data = {
                    "PROMPT_NAME"        : "",
                    "PROMPT_CONTENT"     : ""
                }
                
                col1, col2 = st.columns([0.3, 0.7])

                with col1:
                    name = st.text_input("Name", value=prompt_data["PROMPT_NAME"], max_chars=40)
                with col2:
                    content = st.text_area("Content", value=prompt_data["PROMPT_CONTENT"], height=200, max_chars=4000)

                btn_col1, btn_col2, btn_col3 = st.columns([2, 2.2, 6])

                if btn_col1.button("Save", type="primary", use_container_width=False):
                    try:
                        component.get_processing(True)
                        if mode == "create":
                            msg, _ = db_prompt_service.insert_prompt(
                                prompt_name=name,
                                prompt_content=content,
                                user_id=user_id
                            )
                            component.get_success(msg, ":material/add_row_below:")

                    except Exception as e:
                        component.get_error(f"[Error] Creating Prompt:\n{e}")
                    finally:
                        component.get_processing(False)
                        st.session_state["show_form_prompts"] = False
                        st.rerun()                 
