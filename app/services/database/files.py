python
import streamlit as st
import pandas as pd
from services.database.connection import Connection

class FileService:
    """
    Service class for handling all operations related to files (FILES).
    """
    def __init__(self):
        """
        Initializes the FileService with a shared database connection instance.
        """
        self.conn_instance = Connection()

    @property
    def conn(self):
        """
        Property that always returns a valid database connection.
        Ensures reconnection if the connection was dropped.
        """
        return self.conn_instance.get_connection()

    @st.cache_data
    def get_all_files(self, user_id):
        """
        Retrieves all files associated with a user, including OWNER status, username, email, and user count.

        Args:
            user_id (int): The ID of the user.

        Returns:
            pd.DataFrame: A DataFrame containing file information.
        """
        query = """
            SELECT 
                A.FILE_ID,
                A.MODULE_ID,
                B.MODULE_NAME,
                B.MODULE_VECTOR_STORE,
                A.FILE_SRC_FILE_NAME,
                A.FILE_SRC_SIZE,
                A.FILE_SRC_STRATEGY,
                CASE 
                    WHEN B.MODULE_VECTOR_STORE = 0 THEN NULL 
                    ELSE A.FILE_TRG_OBJ_NAME 
                END AS FILE_TRG_OBJ_NAME,
                A.FILE_TRG_EXTRACTION,
                A.FILE_TRG_TOT_PAGES,
                A.FILE_TRG_TOT_CHARACTERS,
                A.FILE_TRG_TOT_TIME,
                A.FILE_TRG_LANGUAGE,
                A.FILE_TRG_PII,
                A.FILE_DESCRIPTION,
                A.FILE_VERSION,
                A.FILE_DATE,
                A.FILE_STATE,
                FU1.USER_ID,
                U1.USER_GROUP_ID,
                FU2.OWNER,
                FU2.USER_ID AS USER_ID_OWNER,
                U2.USER_USERNAME,
                U2.USER_EMAIL,
                (
                    SELECT COUNT(1)
                    FROM FILE_USER FU3
                    WHERE FU3.FILE_ID = A.FILE_ID
                    AND FU3.OWNER <> 1
                ) AS FILE_USERS
            FROM
                FILES A
            LEFT JOIN
                MODULES B
                ON B.MODULE_ID = A.MODULE_ID
            JOIN
                FILE_USER FU1
                ON FU1.FILE_ID = A.FILE_ID
                AND FU1.USER_ID = :user_id
            JOIN
                USERS U1
                ON U1.USER_ID = FU1.USER_ID
            JOIN
                FILE_USER FU2
                ON FU2.FILE_ID = A.FILE_ID
                AND FU2.OWNER = 1
            JOIN
                USERS U2
                ON U2.USER_ID = FU2.USER_ID
            WHERE
                A.FILE_STATE <> 0
            ORDER BY
                A.FILE_ID DESC
        """
        return pd.read_sql(query, con=self.conn, params={"user_id": user_id})

    def delete_file_user_by_user(self, file_id, user_id, file_name):
        delete_query = """
            DELETE FROM FILE_USER
            WHERE FILE_ID = :file_id AND USER_ID = :user_id
        """
        with self.conn.cursor() as cur:
            cur.execute(delete_query, {
                "file_id": file_id,
                "user_id": user_id
            })

        self.conn.commit()
        return f"You have been removed from access to file **{file_name}**."
    
    def insert_file(
            self,
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
        ):
        """
        Inserts or updates a file record and its user association.
        """

        check_query = """
            SELECT FILE_ID, FILE_VERSION
            FROM FILES
            WHERE FILE_SRC_FILE_NAME = :file_src_file_name
            AND MODULE_ID = :module_id
            AND FILE_TRG_PII = :file_trg_pii
        """
        df = pd.read_sql(
            check_query,
            con=self.conn,
            params={
                "file_src_file_name": file_src_file_name,
                "module_id": module_id,
                "file_trg_pii": file_trg_pii
            }
        )

        with self.conn.cursor() as cur:
            if not df.empty:
                file_id = df['FILE_ID'].iloc[0]
                file_version = df['FILE_VERSION'].iloc[0]

                user_file_query = """
                    SELECT 1 FROM FILE_USER
                    WHERE FILE_ID = :file_id AND USER_ID = :user_id
                """
                df_user_file = pd.read_sql(
                    user_file_query,
                    con=self.conn,
                    params={
                        "file_id": file_id,
                        "user_id": user_id
                    }
                )

                if not df_user_file.empty:
                    cur.execute("""
                        UPDATE FILES SET
                            FILE_SRC_SIZE      = :file_src_size,
                            FILE_SRC_STRATEGY  = :file_src_strategy,
                            FILE_TRG_LANGUAGE  = :file_trg_language,
                            FILE_VERSION       = :file_version_new,
                            FILE_DESCRIPTION   = :file_description,
                            FILE_STATE         = 1,
                            FILE_DATE          = SYSDATE
                        WHERE FILE_ID = :file_id
                    """, {
                        "file_src_size": file_src_size,
                        "file_src_strategy": file_src_strategy,
                        "file_trg_language": file_trg_language,
                        "file_version_new": file_version + 1,
                        "file_description": file_description,
                        "file_id": file_id
                    })

                    cur.execute("DELETE FROM DOCS WHERE FILE_ID = :file_id", {"file_id": file_id})

                    self.conn.commit()
                    return f"File '{file_name}' already existed and added new version.", int(file_id)

                else:
                    cur.execute("""
                        INSERT INTO FILE_USER (FILE_ID, USER_ID, OWNER)
                        VALUES (:file_id, :user_id, 0)
                    """, {
                        "file_id": file_id,
                        "user_id": user_id
                    })
                    self.conn.commit()

                    return f"File '{file_name}' existed but was linked to user.", file_id

            else:
                new_file_id_var = cur.var(int)
                cur.execute("""
                    INSERT INTO FILES (
                        MODULE_ID,
                        FILE_SRC_FILE_NAME,
                        FILE_SRC_SIZE,
                        FILE_SRC_STRATEGY,
                        FILE_TRG_OBJ_NAME,
                        FILE_TRG_LANGUAGE,
                        FILE_TRG_PII,
                        FILE_DESCRIPTION,
                        FILE_VERSION,
                        FILE_DATE,
                        FILE_STATE
                    ) VALUES (
                        :module_id,
                        :file_src_file_name,
                        :file_src_size,
                        :file_src_strategy,
                        :file_trg_obj_name,
                        :file_trg_language,
                        :file_trg_pii,
                        :file_description,
                        1,
                        SYSDATE,
                        1
                    ) RETURNING FILE_ID INTO :new_file_id
                """, {
                    "module_id": module_id,
                    "file_src_file_name": file_src_file_name,
                    "file_src_size": file_src_size,
                    "file_src_strategy": file_src_strategy,
                    "file_trg_obj_name": file_trg_obj_name,
                    "file_trg_language": file_trg_language,
                    "file_trg_pii": file_trg_pii,
                    "file_description": file_description,
                    "new_file_id": new_file_id_var
                })

                file_id_new = new_file_id_var.getvalue()[0]

                cur.execute("""
                    INSERT INTO FILE_USER (FILE_ID, USER_ID, OWNER)
                    VALUES (:file_id, :user_id, 1)
                """, {
                    "file_id": file_id_new,
                    "user_id": user_id
                })
                self.conn.commit()

                return f"File '{file_name}' has been created successfully.", file_id_new

    
    def update_extraction(
            self,
            file_id,
            file_trg_extraction
        ):
        """
        Updates the file extraction information in the database.
        Replaces the existing extraction content with the new content.

        Args:
            file_id (int)             : ID of the file to update.
            file_trg_extraction (str) : Extraction content to update.

        Returns:
            str: Success message.
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE FILES SET
                    FILE_TRG_EXTRACTION = :file_trg_extraction
                WHERE FILE_ID = :file_id
            """, {
                "file_trg_extraction": file_trg_extraction,
                "file_id": file_id
            })
        self.conn.commit()
        return "File extraction has been updated successfully."

    def update_file(
            self,
            file_id,
            file_trg_obj_name,
            file_trg_tot_pages,
            file_trg_tot_characters,
            file_trg_tot_time,
            file_trg_language
        ):
        """
        Updates the file information in the database.

        Args:
            file_id (int)                 : ID of the file to update.
            file_trg_obj_name (str)       : Target object name.
            file_trg_tot_pages (int)      : Total number of pages.
            file_trg_tot_characters (int) : Total number of characters.
            file_trg_tot_time (str)       : Total processing time.
            file_trg_language (str)       : Language of the file.

        Returns:
            str: Success message.
        """
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE FILES SET
                    FILE_TRG_OBJ_NAME       = :file_trg_obj_name,
                    FILE_TRG_TOT_PAGES      = :file_trg_tot_pages,
                    FILE_TRG_TOT_CHARACTERS = :file_trg_tot_characters,
                    FILE_TRG_TOT_TIME       = :file_trg_tot_time,
                    FILE_TRG_LANGUAGE       = :file_trg_language
                WHERE FILE_ID = :file_id
            """, {
                "file_trg_obj_name": file_trg_obj_name,
                "file_trg_tot_pages": file_trg_tot_pages,
                "file_trg_tot_characters": file_trg_tot_characters,
                "file_trg_tot_time": file_trg_tot_time,
                "file_trg_language": file_trg_language,
                "file_id": file_id
            })
        self.conn.commit()
        return "The file was updated successfully."


    def delete_file(self, file_name, file_id):
        """
        Deletes a file and its associations from FILES, FILE_USER, and DOCS tables.

        Args:
            file_name (str): Name of the file to delete.
            file_id (int): ID of the file to delete.

        Returns:
            str: Success or error message.
        """
        query_check = """
            SELECT FILE_ID FROM FILES
            WHERE FILE_ID = :file_id AND FILE_STATE <> 0
        """
        df = pd.read_sql(query_check, con=self.conn, params={"file_id": file_id})

        if df.empty:
            return f"File '{file_name}' does not exist or is already deleted."

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM DOCS WHERE FILE_ID = :file_id
                """, {"file_id": file_id})

                cur.execute("""
                    DELETE FROM FILE_USER WHERE FILE_ID = :file_id
                """, {"file_id": file_id})

                cur.execute("""
                    DELETE FROM FILES WHERE FILE_ID = :file_id
                """, {"file_id": file_id})

            self.conn.commit()
            return f"File '{file_name}' and all related records have been deleted successfully."

        except Exception as e:
            self.conn.rollback()
            return f"[Error] Failed to delete file '{file_name}': {str(e)}"

        
    def update_file_user(self, file_id, user_ids):
        """
        Updates the FILE_USER table for a given FILE_ID by replacing the existing non-owner users.

        Args:
            file_id (int): The file ID to update.
            user_ids (list): List of user IDs to assign to this file (shared users).

        Returns:
            str: Success message.
        """
        delete_query = """
            DELETE FROM FILE_USER
            WHERE FILE_ID = :file_id AND OWNER = 0
        """
        with self.conn.cursor() as cur:
            cur.execute(delete_query, {"file_id": file_id})
        
            insert_query = """
                INSERT INTO FILE_USER (FILE_USER_ID, FILE_ID, USER_ID, OWNER)
                VALUES (FILE_USER_ID_SEQ.NEXTVAL, :file_id, :user_id, 0)
            """
            for user_id in user_ids:
                cur.execute(insert_query, {"file_id": file_id, "user_id": user_id})
        
        self.conn.commit()
        return f"File User relations for File ID [{file_id}] updated successfully."

    
    def delete_file_user(self, file_user_id):
        """
        Deletes a record from FILE_USER.
        """
        query = """
            DELETE FROM FILE_USER WHERE FILE_USER_ID = :file_user_id
        """
        with self.conn.cursor() as cur:
            cur.execute(query, {"file_user_id": file_user_id})
        self.conn.commit()
        return f"Shared FileUser ID {file_user_id} deleted successfully."

    def get_all_file_user_cache(self, user_id, force_update=False):
        if force_update:
            self.get_all_file_user.clear()
        return self.get_all_file_user(user_id)

    @st.cache_data
    def get_all_file_user(self, user_id):
        """
        Retrieves FILE_USER records for files shared with other users (excluding current user_id).

        Args:
            user_id (int): The ID of the current user.

        Returns:
            pd.DataFrame: Shared FILE_USER records (excluding files belonging to user_id).
        """
        query = """
            SELECT 
                FU.FILE_USER_ID,
                FU.FILE_ID,
                F.FILE_SRC_FILE_NAME,
                F.FILE_DESCRIPTION,
                FU.USER_ID,
                U.USER_USERNAME,
                U.USER_NAME || ', ' || U.USER_LAST_NAME AS USER_FULL_NAME,
                UG.USER_GROUP_ID,
                UG.USER_GROUP_NAME,
                FU.OWNER,
                FU.FILE_USER_STATE,
                FU.FILE_USER_DATE
            FROM
                FILE_USER FU
            JOIN FILES F 
                ON FU.FILE_ID = F.FILE_ID
            JOIN USERS U
                ON FU.USER_ID = U.USER_ID
            JOIN USER_GROUP UG
                ON U.USER_GROUP_ID = UG.USER_GROUP_ID
            WHERE
                FU.USER_ID <> :user_id
                AND FU.OWNER <> 1
                AND F.FILE_STATE <> 0
            ORDER BY
                FU.FILE_USER_ID
        """
        return pd.read_sql(query, con=self.conn, params={"user_id": user_id})