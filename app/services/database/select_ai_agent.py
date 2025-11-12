import streamlit as st
import pandas as pd
from services.database.connection import Connection

class SelectAIAgentService:
    """
    Service class for managing Select AI operations.
    """

    def __init__(self):
        """
        Initializes the SelectAIService with a shared database connection.
        """
        self.conn_instance = Connection()
        self.conn = self.conn_instance.get_connection()

    def create_agent(
            self,
            profile_name_sql,
            p_profile_name_rag
        ):
        """
        Creates an agent for Select AI in the database.

        Args:
            profile_name_sql (str): The name of the SQL profile to create.
            p_profile_name_rag (str): The name of the RAG profile to create.
        """
        with self.conn.cursor() as cur:
            query = f"""
                BEGIN
                    SP_SEL_AI_AGENT('{profile_name_sql}', '{p_profile_name_rag}');
                END;
            """
            cur.execute(query)
        self.conn.commit()
        return f"[Select AI Agent]: Module executed successfully."
    
    def get_tables_cache(self, user_id, force_update=False):
        if force_update:
            # Borra la caché de la función
            self.get_tables.clear()
        return self.get_tables(user_id)
    
    @st.cache_data
    def get_tables(_self, user_id):        
        """
        Retrieves metadata for tables associated with the Select AI module.

        Returns:
            pd.DataFrame: A DataFrame containing table metadata, including columns and comments.
        """
        query = f"""
            SELECT 
                t.owner,
                t.table_name,
                c.column_name,
                c.data_type,
                cc.comments
            FROM 
                all_tables t
            JOIN 
                all_tab_columns c
                ON t.table_name = c.table_name AND t.owner = c.owner
            LEFT JOIN 
                all_col_comments cc
                ON c.table_name = cc.table_name 
                AND c.owner = cc.owner 
                AND c.column_name = cc.column_name
            WHERE 
                (UPPER(t.owner), UPPER(t.table_name)) IN (
                    SELECT 
                        UPPER(SUBSTR(F.FILE_TRG_OBJ_NAME, 1, INSTR(F.FILE_TRG_OBJ_NAME, '.') - 1)) AS owner,
                        UPPER(SUBSTR(F.FILE_TRG_OBJ_NAME, INSTR(F.FILE_TRG_OBJ_NAME, '.') + 1)) AS table_name
                    FROM FILES F
                    JOIN FILE_USER FU ON F.FILE_ID = FU.FILE_ID
                    WHERE 
                        F.MODULE_ID = 1 
                        AND F.FILE_STATE = 1 
                        AND FU.USER_ID = {user_id}
                )
            ORDER BY 
                t.owner, t.table_name, c.column_id
        """
        return pd.read_sql(query, con=_self.conn)

    def get_data(self, sql):
        """
        Ejecuta el SQL recibido y devuelve el DataFrame completo sin modificaciones.
        """
        try:
            return pd.read_sql(sql, con=self.conn)
        except Exception:
            return pd.DataFrame()

    def get_conversation(self, profile_name_sql, query):
        """
        Ejecuta la función SP_SEL_AI_AGENT_CONVERSATION y devuelve el CLOB como cadena.

        Args:
            profile_name_sql (str): Nombre del perfil SQL base para el equipo.
            query (str): Prompt del usuario.

        Returns:
            str: Respuesta del agente (contenido del CLOB)
        """
        # Escapar comillas simples y %
        safe_query = query.replace("'", "''").replace('%', '%%')
        safe_profile = profile_name_sql.replace("'", "''")

        sql = f"""
            SELECT SP_SEL_AI_AGENT_CONVERSATION(
                '{safe_profile}',
                '{safe_query}'
            ) AS ANSWER
            FROM DUAL
        """
        return pd.read_sql(sql, con=self.conn)["ANSWER"].iloc[0].read()