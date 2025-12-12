import time
import json
from datetime import datetime
from textwrap import dedent
from pyarrow import null
import streamlit as st
from annotated_text import annotated_text, annotation
from streamlit_float import *
import pandas as pd

import components as component
import services.database as database
import services as service
import utils as utils

# Initialize service instances
select_ai_service = service.SelectAIService()
db_select_ai_service = database.SelectAIService()
utl_function_service = utils.FunctionService()

# Load login and footer components
st.session_state["page"] = "app_chat_01.py"
login = component.get_login()
component.get_footer()

if login:
    st.set_page_config(layout="centered")
  
    # Get session state variables
    username = st.session_state["username"]
    language = st.session_state["language"]
    user_id = st.session_state["user_id"]
    chat_save = st.session_state["chat-select-ai"]
    profile_name = select_ai_service.get_profile(user_id)
    df_tables = db_select_ai_service.get_tables_cache(user_id)
    
    # Header and description for the application
    st.header(":material/database_search: Select AI")
    st.markdown(f"_Profile Name_ :orange-badge[:material/account_circle: {profile_name}]")
    st.caption("Uses natural-language input with generative AI and vector-search on Oracle AI Database 26ai to query, analyze and act on your data—converting prompts to SQL or chat-style interactions and enabling custom AI agents. [Learn more &rarr;](https://docs.oracle.com/en-us/iaas/autonomous-database-serverless/doc/dbms-cloud-ai-package.html)")
    
    if not df_tables.empty:
        with st.expander("See Tables"):
            # Configure table grouping and field mapping
            group_by_columns = ["OWNER", "TABLE_NAME"]
            fields = {
                "column_name": "COLUMN_NAME",
                "data_type": "DATA_TYPE",
                "comments": "COMMENTS",
                "ui_display": "UI_DISPLAY",
                "classification": "CLASSIFICATION"
            }
            json_tables = utl_function_service.get_tables_json(df_tables, group_by_columns, fields)
            
            st.markdown("**JSON Data (Metadata + Annotations)**")
            st.json(json_tables, expanded=1)

        # Display chat messages from history on app rerun
        for message in st.session_state["chat-select-ai"]:
            if message["role"] == "ai":
                with st.chat_message(message["role"], avatar="images/llm_meta.svg"):
                    # Render Select AI response
                    response_time = message.get("response_time", "N/A")
                    annotated_text(annotation("Select AI", response_time, background="#484c54", color="#ffffff"))
                    st.markdown(message.get("response", message.get("narrate", "")))

                    # Render Analytics visualization if available
                    if message.get("analytics"):
                        analytics_time = message.get("analytics_time", "N/A")
                        annotated_text(annotation("Analytics Agent", analytics_time, background="#484c54", color="#ffffff"))
                        df = message["analytics_df"]
                        exec(message["analytics"])
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
            assistant_message = st.chat_message("ai", avatar="images/llm_meta.svg")
            placeholder = assistant_message.empty()

            # Build response with consistent formatting
            with placeholder.container():
                # Step 1: Get Select AI response based on selected action
                with st.spinner("Wait for Select AI...", show_time=True):
                    start_time = time.time()
                    action = st.session_state.get("select_ai_action", "narrate")
                    response = db_select_ai_service.get_chat(prompt, profile_name, action, language)
                    response_time = f"{(time.time() - start_time) * 1000:.2f} ms"
                    annotated_text(annotation("Select AI", response_time, background="#484c54", color="#ffffff"))
                
                # Check if response is an error message
                error_indicators = ["Sorry,", "Lo siento,", "Desculpe,", "Error al generar", "Error while generating", "Erro ao gerar"]
                is_error = any(response.startswith(indicator) for indicator in error_indicators)
                
                # Process valid response (not an error)
                if not is_error:
                    st.markdown(response)

                    # Initialize analytics variables
                    analytics_df = null
                    analytics = ""
                    analytics_time = "00:00:00"
                    
                    # Step 2: Analytics Agent (if enabled)
                    if st.session_state.get("analytics_agent", False):
                        with st.spinner("Wait for Analytics Agent...", show_time=True):
                            time.sleep(2)
                            start_time = time.time()
                            
                            # Get SQL query from Select AI (only if not already showsql action)
                            if action != "showsql":
                                sql_query = db_select_ai_service.get_chat(prompt, profile_name, 'showsql', language)
                            else:
                                sql_query = response
                            
                            # Execute SQL query and get DataFrame
                            df = db_select_ai_service.get_data(sql_query)
                            analytics_df = df
                            selected_agent_id = int(st.session_state.get("selected_agent_id"))
                            time.sleep(2)
                            
                            # Build enriched prompt with DataFrame metadata
                            df_metadata = {
                                "columns": list(df.columns),
                                "shape": {"rows": df.shape[0], "cols": df.shape[1]},
                                "dtypes": {col: str(df[col].dtype) for col in df.columns}
                            }
                            
                            enriched_prompt = dedent(f"""
                                SQL Query:
                                {sql_query}

                                DataFrame Result Metadata:
                                - Columns: {df_metadata['columns']}
                                - Shape: {df_metadata['shape']['rows']} rows x {df_metadata['shape']['cols']} columns
                                - Data types: {df_metadata['dtypes']}

                                Sample data (first 3 rows):
                                {df.head(3).to_string()}

                                Generate Python code using Streamlit to visualize this data. Use ONLY the column names that 
                                exist in the DataFrame. If the result is a single aggregated value, use st.metric() instead of charts.
                            """).strip()
                            
                            # Get analytics code from Generative AI agent
                            analytics_raw = service.GenerativeAIService.get_agent(user_id, selected_agent_id, enriched_prompt)

                            # Handle service busy scenario
                            if "Service busy. Please try again later." in analytics_raw:
                                st.warning("Service busy. Please try again later.", icon=":material/schedule:")
                                analytics = ""
                            else:
                                # Clean up code blocks from analytics response
                                analytics = analytics_raw.replace("```python", "").replace("```", "")

                            analytics_time = f"{(time.time() - start_time) * 1000:.2f} ms"
                            annotated_text(annotation("Analytics Agent", analytics_time, background="#484c54", color="#ffffff"))
                            
                            # Execute analytics code if available
                            if analytics:
                                exec(analytics)
                
                # Handle error response
                else:
                    analytics_df = null
                    analytics = ""
                    analytics_time = "00:00:00"
                    st.warning(response, icon=":material/error:")
                
                st.markdown("\n")
                
                # Save chat data to session state
                chat_data = {
                    "role": "ai",
                    "response": response,
                    "response_time": response_time,
                    "analytics_df": analytics_df,
                    "analytics": analytics,
                    "analytics_time": analytics_time
                }
                chat_save.append(chat_data)
                st.session_state["chat-select-ai"] = chat_save
        
    else:
        st.info("Upload file for this module.", icon=":material/info:")