import streamlit as st
import pandas as pd
from services.database.connection import Connection

class PromptService:
    """
    Service class for handling all operations related to modules.
    """

    def __init__(self):
        """
        Initializes the ModuleService with a shared database connection instance.
        """
        self.conn_instance = Connection()
        self.conn = self.conn_instance.get_connection()

    def get_all_prompts_cache(self, user_id, force_update=False):
        """
        Cached wrapper to retrieve prompts assigned to specific user_id.
        """
        if force_update:
            self.get_all_prompts.clear()
        return self.get_all_prompts(user_id)

    @st.cache_data
    def get_all_prompts(_self, user_id):
        """
        Retrieves all prompts assigned to the provided user_id, with model information included.

        Args:
            user_id (int): The ID of the user.

        Returns:
            pd.DataFrame: List of prompts assigned to user_id with model details.
        """
        query = f"""
            SELECT 
                P.PROMPT_ID,
                P.PROMPT_NAME,
                P.PROMPT_CONTENT                            
            FROM 
                PROMPTS P
            LEFT JOIN
                PROMPT_USER PU
                ON PU.PROMPT_ID = P.PROMPT_ID
                AND PU.USER_ID = {user_id}
        """
        return pd.read_sql(query, con=_self.conn)
    
    def insert_prompt(self, prompt_name, prompt_content, user_id):
        """"
        Inserts a new prompt into the database. If prompt name already exists, aborts.
        """
        # Validates if an existing prompt with same name exists
        query = f"""
            SELECT 1 FROM PROMPTS
            WHERE PROMPT_NAME = '{prompt_name}'
        """
        df = pd.read_sql(query, con=self.conn)

        if not df.empty:
            raise ValueError(f"Prompt '{prompt_name}' already exists. Please choose a different name.")
        
        # Inserts the new prompt
        with self.conn.cursor() as cur:
            prompt_id_var = cur.var(int)
            cur.execute(f"""
                INSERT INTO PROMPTS (
                    PROMPT_NAME,
                    PROMPT_CONTENT
                ) VALUES (
                    '{prompt_name}',
                    '{prompt_content}'
                ) RETURNING PROMPT_ID INTO :prompt_id
            """, {
                "prompt_id": prompt_id_var
            })
        self.conn.commit()

        prompt_id = prompt_id_var.getvalue()[0] 

        # Inserts the relation PROMPT_USER
        with self.conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO PROMPT_USER (PROMPT_ID, USER_ID)
                VALUES ({prompt_id}, {user_id})
            """)
        self.conn.commit()

        return f"Prompt '{prompt_name}' has been created successfully.", prompt_id
    
