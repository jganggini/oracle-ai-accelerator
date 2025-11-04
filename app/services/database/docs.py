import os
from services.database.connection import Connection

from langchain_community.embeddings.oci_generative_ai import OCIGenAIEmbeddings
from langchain_community.vectorstores import OracleVS

class DocService:
    """
    Service class for interacting with the document-related database operations.
    """

    def __init__(self):
        """
        Keep only the singleton instance; fetch a live connection on-demand
        to avoid using expired database connections.
        """
        self.conn_instance = Connection()

    @property
    def conn(self):
        """Always returns a live connection (auto-reconnect)."""
        return self.conn_instance.get_connection()
    
    def vector_store(self, file_id):
        """
        Executes a stored procedure to add a document to the vector store.

        Args:
            file_id (str): The identifier of the file to be stored in the vector store.

        Returns:
            str: Confirmation message indicating the document was stored successfully.
        """
        
        query = f"""
                BEGIN
                    SP_VECTOR_STORE('{file_id}');
                END;
            """
        conn = self.conn
        with conn.cursor() as cur:
            cur.execute(query)
        conn.commit()
        return f"The file was created to the vector store successfully."
    
    def get_vector_store(self):
        """
        Creates and returns an Oracle Vector Store instance using OCI Generative AI embeddings.

        Returns:
            OracleVS: The vector store instance.
        """
        embeddings = OCIGenAIEmbeddings(
            model_id         = os.getenv('CON_GEN_AI_EMB_MODEL_ID'),
            service_endpoint = os.getenv('CON_GEN_AI_SERVICE_ENDPOINT'),
            compartment_id   = os.getenv('CON_COMPARTMENT_ID')
        )
        
        conn = self.conn
        return OracleVS(
            client             = conn,
            embedding_function = embeddings,
            table_name         = 'docs'
        )