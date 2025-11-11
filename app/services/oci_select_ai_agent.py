import os
import time

from dotenv import load_dotenv
import components as component
import services.database as database

# Initialize the service
db_select_ai_agent_service = database.SelectAIAgentService()

load_dotenv()

class SelectAIAgentService:
            
    @staticmethod
    def create(
            profile_name_sql,
            profile_name_rag
        ):
        """
        Creates a table from a CSV file and updates it with comments, then creates a profile.

        Args:
            profile_name_sql (str): The name of the SQL profile.
            profile_name_rag (str): The name of the RAG profile.
        """
        try:            
            # Create Agent
            db_select_ai_agent_service.create_agent(
                profile_name_sql,
                profile_name_rag
            )

            return f"[Select AI Agent]: Module executed successfully."
        except Exception as e:
            component.get_error(f"[Error] Select AI Agent: {e}")
    
    @staticmethod
    def get_conversation(
            profile_name_sql,
            query
        ):
        """
        Gets a conversation from the Select AI Agent.

        Args:
            profile_name_sql (str): The name of the SQL profile.
            query (str): The query to get the conversation.
        """
        try:
            # Get Conversation
            return db_select_ai_agent_service.get_conversation(
                profile_name_sql,
                query
            )
        except Exception as e:
            component.get_error(f"[Error] Select AI Agent - Get Conversation: {e}")