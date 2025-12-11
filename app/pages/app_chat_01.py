import time
import json
from datetime import datetime
from pyarrow import null
import streamlit as st
from annotated_text import annotated_text, annotation
from streamlit_float import *
import pandas as pd

import components as component
import services.database as database
import services as service
import utils as utils

# Crear una instancia del servicio
select_ai_service = service.SelectAIService()
db_select_ai_service = database.SelectAIService()
utl_function_service = utils.FunctionService()

# Load login and footer components
st.session_state["page"] = "app_chat_01.py"
login = component.get_login()
component.get_footer()

if login:
    st.set_page_config(layout="centered")
  
    username     = st.session_state["username"]
    language     = st.session_state["language"]
    user_id      = st.session_state["user_id"]
    chat_save    = st.session_state["chat-select-ai"]
    profile_name = select_ai_service.get_profile(user_id)
    df_tables    = db_select_ai_service.get_tables_cache(user_id)
    
    # Header and description for the application
    st.header(":material/database_search: Select AI")
    st.markdown("_Profile Name_ :orange-badge[:material/account_circle: "+ profile_name +"]")
    st.caption("Uses natural-language input with generative AI and vector-search on Oracle AI Database 26ai to query, analyze and act on your data—converting prompts to SQL or chat-style interactions and enabling custom AI agents. [Learn more &rarr;](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/dbms-cloud-ai-package.html)")
    
    if not df_tables.empty:
        with st.expander("See Tables"):
            # Configurar los parámetros
            group_by_columns = ["OWNER", "TABLE_NAME"]
            fields = {
                "column_name"    : "COLUMN_NAME",
                "data_type"      : "DATA_TYPE",
                "comments"       : "COMMENTS",
                "ui_display"     : "UI_DISPLAY",
                "classification" : "CLASSIFICATION"
            }
            json_tables = utl_function_service.get_tables_json(df_tables, group_by_columns, fields)
            
            st.markdown("**Json Data (Metadata + Annotations)**")
            st.json(json_tables, expanded=1)

        # Display chat messages from history on app rerun
        for message in st.session_state["chat-select-ai"]:
            if message["role"] == "ai":
                with st.chat_message(message["role"], avatar="images/llm_aix.svg"):
                    # Render each section of the stored response
                    annotated_text(annotation("Select AI Agent", message["narrate_time"], background="#484c54", color="#ffffff"))
                    st.markdown(message["narrate"])

                    if message.get("showsql"):
                        annotated_text(annotation("Analytics Agent", message["showsql_time"], background="#484c54", color="#ffffff"))
                        df = message["analytics_df"]
                        exec(message["analytics"])

                    if message.get("ExplainSQL"):
                        annotated_text(annotation("Explain Agent", message["explainsql_time"], background="#484c54", color="#ffffff"))
                        st.markdown(message["explainsql"])
            else:
                with st.chat_message(message["role"], avatar=":material/psychology:"):
                    st.markdown(message["content"])
            st.markdown("\n\n")

        # React to user input
        if prompt := st.chat_input("What is up?"):
            # Display user message in chat message container
            st.chat_message("human", avatar=":material/psychology:").markdown(prompt)
            
            # Add user message to chat history
            st.session_state["chat-select-ai"].append({"role": "human", "content": prompt})

            # Create placeholders for progressive updates
            assistant_message = st.chat_message("ai", avatar="images/llm_aix.svg")
            placeholder = assistant_message.empty()

            # Build response with consistent formatting
            with placeholder.container():
                # Fetch narrate with timing
                with st.spinner("Wait for Select AI Agent...", show_time=True):
                    start_time = time.time()
                    action     = st.session_state.get("select_ai_action", "narrate")
                    narrate = db_select_ai_service.get_chat(
                        prompt,
                        profile_name,
                        action,
                        language
                    )
                    # narrate
                    narrate_time = f"{(time.time() - start_time) * 1000:.2f} ms"
                    annotated_text(annotation("Select AI Agent", narrate_time, background="#484c54", color="#ffffff"))
                
                if "NNN" not in narrate:
                    # narrate
                    st.markdown(narrate)

                    # Defaults to avoid undefined variables when toggles are off
                    showsql         = ""
                    analytics_df    = null
                    analytics       = ""
                    showsql_time    = "00:00:00"
                    explainsql      = ""
                    explainsql_time = "00:00:00"
                    
                    # Agent Analysis
                    if st.session_state.get("analytics_agent", False):
                        with st.spinner("Wait for Analytics Agent...", show_time=True):
                            time.sleep(2)
                            start_time = time.time()
                            action     = 'showsql'
                            showsql    = db_select_ai_service.get_chat(
                                prompt,
                                profile_name,
                                action,
                                language
                            )
                            
                            # Execute the SQL query, convert results to DataFrame, and display a bar chart
                            df = db_select_ai_service.get_data(showsql)
                            analytics_df = df
                            selected_agent_id = int(st.session_state.get("selected_agent_id"))
                            time.sleep(2)
                            analytics_raw = service.GenerativeAIService.get_agent(user_id, selected_agent_id, showsql)

                            print(analytics_raw)
                            print("--------------------------------")

                            # Si el servicio está ocupado, mostramos mensaje controlado y evitamos ejecutar código
                            if "Service busy. Please try again later." in analytics_raw:
                                st.warning("Service busy. Please try again later.", icon=":material/schedule:")
                                analytics = ""
                            else:
                                # Remove ```python and ``` from the analytics code if present
                                analytics = analytics_raw.replace("```python", "").replace("```", "")

                            showsql_time = f"{(time.time() - start_time) * 1000:.2f} ms"
                            annotated_text(annotation("Analytics Agent", showsql_time, background="#484c54", color="#ffffff"))
                            
                            print(showsql)
                            print(df)
                            print(analytics)
                            print("--------------------------------")
                            if analytics:
                                exec(analytics)

                    # explainsql
                    if st.session_state.get("sql_explain_agent", False):
                        with st.spinner("Wait for SQL Explain Agent...", show_time=True):
                            # Ensure showsql is computed even if Agent Analysis is off
                            if not showsql:
                                time.sleep(2)
                                start_time_showsql = time.time()
                                action             = 'showsql'
                                showsql            = db_select_ai_service.get_chat(
                                    prompt,
                                    profile_name,
                                    action,
                                    language
                                )
                                showsql_time = f"{(time.time() - start_time_showsql) * 1000:.2f} ms"

                            start_time = time.time()
                            prompt     = showsql
                            action     = 'explainsql'
                            explainsql = db_select_ai_service.get_chat(
                                prompt,
                                profile_name,
                                action,
                                language
                            )
                            explainsql_time = f"{(time.time() - start_time) * 1000:.2f} ms"
                            annotated_text(annotation("Explain Agent", explainsql_time, background="#484c54", color="#ffffff"))
                            st.markdown(explainsql)
                
                else:
                    # narrate
                    narrate         = st.session_state["language-message"]
                    narrate_time    = narrate_time
                    showsql         = ""
                    analytics_df    = null
                    analytics       = ""
                    showsql_time    = "00:00:00"
                    explainsql      = "",
                    explainsql_time = "00:00:00"

                    st.markdown(narrate)
                
                st.markdown("\n\n")
                
                # Guarda el bloque de datos en formato JSON
                chat_data = {
                    "role"            : "ai",
                    "narrate"         : narrate,
                    "narrate_time"    : narrate_time,
                    "showsql"         : showsql,
                    "analytics_df"    : analytics_df,
                    "analytics"       : analytics,
                    "showsql_time"    : showsql_time,
                    "explainsql"      : explainsql,
                    "explainsql_time" : explainsql_time
                }
                chat_save.append(chat_data)

                st.session_state["chat-select-ai"] = chat_save
        
    else:
        st.info("Upload file for this module.", icon=":material/info:")