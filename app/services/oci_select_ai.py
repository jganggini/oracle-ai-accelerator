import os
import time

from dotenv import load_dotenv
import components as component
import services.database as database

# Initialize the service
db_select_ai_service = database.SelectAIService()

load_dotenv()

class SelectAIService:

    @staticmethod
    def get_profile(user_id: int) -> str:
        """
        Generates a profile name for the given user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            str: The generated profile name.
        """
        credential_name = os.getenv('CON_ADB_DEV_C_CREDENTIAL_NAME') 
        return (f"{credential_name}_SQL_{str(user_id)}").upper()
    
    @staticmethod
    def create_profile(user_id):   
        """
        Creates a profile for Select AI.

        Args:
            user_id (int): The ID of the user.
        """
        try:
            profile_name = SelectAIService.get_profile(user_id)
        
            # Create Profile
            db_select_ai_service.create_profile(
                profile_name,
                user_id
            )
            component.get_success("[Select AI] Profile was created successfully.", ":material/person_add:")
        except Exception as e:
            component.get_error(f"[Error] Select AI - Create Profile:\n{e}")
        
    @staticmethod
    def create(
            user_id,
            file_src_file_name, 
            file_trg_obj_name,
            comment_data_editor,
            file_description=None
        ):
        """
        Creates a table from a CSV file and updates it with comments and annotations, then creates a profile.

        Args:
            user_id (int): The ID of the user.
            file_src_file_name (str): The source file name.
            file_trg_obj_name (str): The target table name.
            comment_data_editor (pd.DataFrame): DataFrame containing comments and annotations to update.
            file_description (str, optional): Description to add as table annotation. Defaults to None.

        Returns:
            str: A success message if the operation is completed successfully.
        """
        try:
            profile_name = SelectAIService.get_profile(user_id)
            object_uri   = file_src_file_name
            table_name   = file_trg_obj_name
            
            # Create table
            db_select_ai_service.create_table_from_csv(
                object_uri,
                table_name
            ) 
            component.get_toast(f"Table '{table_name}' has been created successfully.", ":material/database:")

            # Process comments
            comments_added = 0
            if comment_data_editor is not None and not comment_data_editor.empty:
                for _, row in comment_data_editor.iterrows():
                    # Only update if the comment is not empty
                    if row["Comment"].strip():
                        db_select_ai_service.update_comment(
                            table_name  = file_trg_obj_name,
                            column_name = row["Column Name"],
                            comment     = row["Comment"]
                        )
                        comments_added += 1
                
                # Show a message if at least one comment was added
                if comments_added > 0:
                    component.get_toast(f"Comment(s) have been added successfully.", ":material/notes:")
            
            # Process column annotations (UI_Display, Classification)
            annotations_added = 0
            if comment_data_editor is not None and not comment_data_editor.empty:
                for _, row in comment_data_editor.iterrows():
                    column_name = row["Column Name"]
                    
                    # Add UI_Display annotation if provided
                    if "UI_Display" in row and row["UI_Display"].strip():
                        db_select_ai_service.update_column_annotation(
                            table_name      = file_trg_obj_name,
                            column_name     = column_name,
                            annotation_name = "UI_Display",
                            annotation_value = row["UI_Display"]
                        )
                        annotations_added += 1
                    
                    # Add Classification annotation if provided
                    if "Classification" in row and row["Classification"].strip():
                        db_select_ai_service.update_column_annotation(
                            table_name      = file_trg_obj_name,
                            column_name     = column_name,
                            annotation_name = "Classification",
                            annotation_value = row["Classification"]
                        )
                        annotations_added += 1
                
                # Show a message if at least one annotation was added
                if annotations_added > 0:
                    component.get_toast(f"Annotation(s) have been added successfully.", ":material/label:")
            
            # Add table-level annotation from file description
            if file_description and file_description.strip():
                db_select_ai_service.update_table_annotation(
                    table_name      = file_trg_obj_name,
                    annotation_name = "UI_Display",
                    annotation_value = file_description
                )
                component.get_toast(f"Table annotation added successfully.", ":material/description:")
            
            # Process PRIMARY KEY constraints
            if comment_data_editor is not None and not comment_data_editor.empty:
                pk_columns = []
                if "Primary Key" in comment_data_editor.columns:
                    for _, row in comment_data_editor.iterrows():
                        if row.get("Primary Key", False):
                            pk_columns.append(row["Column Name"])
                    
                    if pk_columns:
                        db_select_ai_service.add_primary_key(
                            table_name   = file_trg_obj_name,
                            column_names = pk_columns
                        )
                        pk_cols_str = ", ".join(pk_columns)
                        component.get_toast(f"Primary key constraint added on ({pk_cols_str}).", ":material/key:")
            
            # Create Profile
            db_select_ai_service.create_profile(
                profile_name,
                user_id
            )

            db_select_ai_service.get_tables_cache(user_id, force_update=True)

            return f"[Select AI]: Module executed successfully."
        except Exception as e:
            component.get_error(f"[Error] Select AI: {e}")