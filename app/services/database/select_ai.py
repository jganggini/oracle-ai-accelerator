import streamlit as st
import pandas as pd
import oracledb
from services.database.connection import Connection

class SelectAIService:
    """
    Service class for managing Select AI operations.
    """

    def __init__(self):
        """
        Initializes the SelectAIService with a shared database connection.
        """
        self.conn_instance = Connection()
        self.conn = self.conn_instance.get_connection()

    def create_user(self, user_id, password):
        """
        Creates a new database user.

        Args:
            user_id (int): The user_id for the new database user.
            password (str): The password for the new database user.

        Returns:
            str: A message indicating success.
        """
        query = f"""
                CREATE USER SEL_AI_USER_ID_{str(user_id)}
                IDENTIFIED BY "{password}"
                DEFAULT TABLESPACE tablespace
                QUOTA UNLIMITED ON tablespace
            """
        with self.conn.cursor() as cur:
            cur.execute(query)
        self.conn.commit()

        with self.conn.cursor() as cur:
            cur.execute(f"""
                GRANT DWROLE TO SEL_AI_USER_ID_{str(user_id)}
            """)
        self.conn.commit()
        return f"[Select AI]: New User :red[SEL_AI_USER_ID_{str(user_id)}] created successfully for the database."
    
    def drop_user(self, user_id):
        """
        Deletes a database user.

        Args:
            user_id (int): The username of the database user to delete.

        Returns:
            str: A message indicating success.
        """
        try:
            query = f"""
                DROP USER SEL_AI_USER_ID_{str(user_id)} CASCADE
            """
            with self.conn.cursor() as cur:
                cur.execute(query)
            self.conn.commit()
            return f"[Select AI]: The username :red[SEL_AI_USER_ID_{str(user_id)}] of the database user to delete successfully."
        except Exception as e:
            # The username does not exist.
            if 'ORA-01918' in str(e):
                return f"[Select AI]: The username :red[SEL_AI_USER_ID_{str(user_id)}] of the database does not exist."""

    def update_user_password(self, user_id, new_password):
        """
        Updates the password of a database user.

        Args:
            user_id (int): The username of the database.
            new_password (str): The new password to set for the user.

        Returns:
            str: A message indicating the success of the operation.
        """
        with self.conn.cursor() as cur:
            cur.execute(f"""
                ALTER USER SEL_AI_USER_ID_{str(user_id)} IDENTIFIED BY "{new_password}"
            """)
        self.conn.commit()
        return f"[Select AI] The password for user was updated successfully."
    

    def update_comment(
            self,
            table_name,
            column_name,
            comment
        ):
        """
        Updates the comment for a specific column in a table.

        Args:
            table_name (str): The name of the table.
            column_name (str): The name of the column.
            comment (str): The comment to set for the column.
        """
        with self.conn.cursor() as cur:
            cur.execute(f"""
                COMMENT ON COLUMN {table_name}.{column_name} IS '{comment}'
            """)
        self.conn.commit()
    
    def update_column_annotation(
            self,
            table_name,
            column_name,
            annotation_name,
            annotation_value=None
        ):
        """
        Updates an annotation for a specific column in a table.
        If annotation_value is None, adds annotation without value (like SurrogateKey).
        
        Args:
            table_name (str): The name of the table.
            column_name (str): The name of the column.
            annotation_name (str): The name of the annotation.
            annotation_value (str, optional): The value for the annotation. Defaults to None.
        """
        # Escapar comillas simples en el valor si existe
        if annotation_value:
            annotation_value = annotation_value.replace("'", "''")
            annotation_clause = f"{annotation_name} '{annotation_value}'"
        else:
            annotation_clause = annotation_name
        
        with self.conn.cursor() as cur:
            cur.execute(f"""
                ALTER TABLE {table_name} 
                MODIFY ({column_name} ANNOTATIONS (ADD {annotation_clause}))
            """)
        self.conn.commit()
    
    def update_table_annotation(
            self,
            table_name,
            annotation_name,
            annotation_value=None
        ):
        """
        Updates an annotation for a table.
        If annotation_value is None, adds annotation without value.
        
        Args:
            table_name (str): The name of the table.
            annotation_name (str): The name of the annotation.
            annotation_value (str, optional): The value for the annotation. Defaults to None.
        """
        # Escapar comillas simples en el valor si existe
        if annotation_value:
            annotation_value = annotation_value.replace("'", "''")
            annotation_clause = f"{annotation_name} '{annotation_value}'"
        else:
            annotation_clause = annotation_name
        
        with self.conn.cursor() as cur:
            cur.execute(f"""
                ALTER TABLE {table_name} 
                ANNOTATIONS (ADD {annotation_clause})
            """)
        self.conn.commit()
    
    def add_primary_key(
            self,
            table_name,
            column_names
        ):
        """
        Adds a PRIMARY KEY constraint to a table.
        
        Args:
            table_name (str): The name of the table.
            column_names (list): List of column names to include in the primary key.
        """
        if not column_names:
            return
        
        # Unir las columnas en una lista separada por comas
        columns_str = ", ".join(column_names)
        
        # Generar nombre del constraint
        constraint_name = f"PK_{table_name.split('.')[-1]}"
        
        with self.conn.cursor() as cur:
            cur.execute(f"""
                ALTER TABLE {table_name} 
                ADD CONSTRAINT {constraint_name} PRIMARY KEY ({columns_str})
            """)
        self.conn.commit()
    
    def create_table_from_csv(
            self,
            object_uri,
            table_name
        ):
        """
        Creates a table in the database from a CSV file.

        Args:
            object_uri (str): The URI of the CSV file.
            table_name (str): The name of the table to create.
        """    
        with self.conn.cursor() as cur:
            query = f"""
                BEGIN
                    SP_SEL_AI_TBL_CSV('{object_uri}', '{table_name}');
                END;
            """
            cur.execute(query)
        self.conn.commit()

    def create_profile(
            self,
            profile_name,
            user_id
        ):
        """
        Creates a profile for Select AI in the database.

        Args:
            profile_name (str): The name of the profile to create.
            user_id (str): The ID of the user creating the profile.
        """
        with self.conn.cursor() as cur:
            query = f"""
                BEGIN
                    SP_SEL_AI_PROFILE('{profile_name}', {user_id});
                END;
            """
            cur.execute(query)
        self.conn.commit()
    
    def get_chat(
            self,
            prompt,
            profile_name,
            action,
            language
        ):
        """
        Genera una respuesta usando el perfil de Select AI con manejo
        controlado de errores y mensajes en el idioma elegido.
        """
        # Normalizamos el mensaje del usuario para evitar problemas de sintaxis
        prompt = prompt.replace("'", "''")
        prompt = prompt.replace("%", "%%")

        # Indicaciones adicionales para el modelo
        prompt_with_instructions = (
            f"{prompt} /** Do not underline titles. Queries must always be written in uppercase. Answer only in {language}. **/"
        )

        # Mensajes por idioma (simple y directo)
        language_messages = {
            "Spanish": (
                "Lo siento, no se pudo generar una sentencia SQL válida para tu solicitud. "
                "Revisa la consulta e inténtalo de nuevo.",
                "Error al generar la respuesta: "
            ),
            "Portuguese": (
                "Desculpe, não foi possível gerar uma instrução SQL válida para sua solicitação. "
                "Revise a consulta e tente novamente.",
                "Erro ao gerar a resposta: "
            ),
            "English": (
                "Sorry, a valid SQL statement could not be generated for your request. "
                "Please review your query and try again.",
                "Error while generating the response: "
            )
        }
        fallback_sorry, error_prefix = language_messages.get(
            language,
            language_messages["English"]
        )

        # Ejecutamos un bloque PL/SQL que captura excepciones y devuelve el CLOB tal cual
        with self.conn.cursor() as cur:
            response_var = cur.var(oracledb.CLOB)
            cur.execute(
                """
                DECLARE
                    l_sql CLOB;
                BEGIN
                    BEGIN
                        l_sql := DBMS_CLOUD_AI.GENERATE(
                            prompt       => :prompt_text,
                            profile_name => :profile_name,
                            action       => :action
                        );
                        :out_response := l_sql;
                    EXCEPTION
                        WHEN OTHERS THEN
                            :out_response := :error_prefix || SQLERRM;
                    END;
                END;
                """,
                prompt_text=prompt_with_instructions,
                profile_name=profile_name,
                action=action,
                error_prefix=error_prefix,
                out_response=response_var
            )

            response = response_var.getvalue()
            if isinstance(response, oracledb.LOB):
                response = response.read()
            response = response or ""

        # Si Select AI devolvió el mensaje de "Sorry..." lo reemplazamos por el mensaje localizado
        generic_sorry = "Sorry, unfortunately a valid SELECT statement could not be generated"
        if response.startswith(generic_sorry):
            return fallback_sorry

        return response
    
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
            pd.DataFrame: A DataFrame containing table metadata, including columns, comments, and annotations.
        """
        query = f"""
            WITH user_tables AS (
                SELECT 
                    UPPER(SUBSTR(F.FILE_TRG_OBJ_NAME, 1, INSTR(F.FILE_TRG_OBJ_NAME, '.') - 1)) AS owner,
                    UPPER(SUBSTR(F.FILE_TRG_OBJ_NAME, INSTR(F.FILE_TRG_OBJ_NAME, '.') + 1)) AS table_name
                FROM FILES F
                JOIN FILE_USER FU ON F.FILE_ID = FU.FILE_ID
                WHERE 
                    F.MODULE_ID = 1 
                    AND F.FILE_STATE = 1 
                    AND FU.USER_ID = {user_id}
            ),
            annotations_pivot AS (
                SELECT 
                    object_name,
                    column_name,
                    annotation_owner,
                    MAX(CASE WHEN annotation_name = 'UI_DISPLAY' THEN annotation_value END) AS ui_display,
                    MAX(CASE WHEN annotation_name = 'CLASSIFICATION' THEN annotation_value END) AS classification
                FROM all_annotations_usage
                WHERE object_type = 'TABLE'
                AND column_name IS NOT NULL
                GROUP BY object_name, column_name, annotation_owner
            )
            SELECT 
                t.owner,
                t.table_name,
                c.column_name,
                c.data_type,
                cc.comments,
                ap.ui_display,
                ap.classification
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
            LEFT JOIN 
                annotations_pivot ap
                ON c.owner = ap.annotation_owner
                AND c.column_name = ap.column_name
            WHERE 
                (UPPER(t.owner), UPPER(t.table_name)) IN (SELECT owner, table_name FROM user_tables)
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