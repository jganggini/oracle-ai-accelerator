import json
import pandas as pd

from services.database.connection import Connection

class DBMSAIAgentService:
	"""
	Service class for managing DBMS_CLOUD_AI_AGENT objects (TOOL, TASK, AGENT, TEAM).
	"""

	def __init__(self):
		"""
		Initializes the service with a shared database connection.
		"""
		self.conn_instance = Connection()

	@property
	def conn(self):
		"""
		Property that always returns a valid database connection.
		Ensures reconnection if the connection was dropped.
		"""
		return self.conn_instance.get_connection()

	def _to_json_str(self, attributes):
		"""
		Normalize attributes to a JSON string accepted by PL/SQL (CLOB).
		"""
		if attributes is None:
			return "{}"
		if isinstance(attributes, str):
			return attributes
		return json.dumps(attributes, ensure_ascii=False)

	def create_tool(self, p_tool_name, p_attributes):
		"""
		Drop/Create/Enable a TOOL via ORA26AI.SP_AI_TOOL.
		"""
		attrs = self._to_json_str(p_attributes)
		with self.conn.cursor() as cur:
			cur.callproc("ORA26AI.SP_AI_TOOL", [p_tool_name, attrs])
		self.conn.commit()

	def create_task(self, p_task_name, p_attributes):
		"""
		Drop/Create/Enable a TASK via ORA26AI.SP_AI_TASK.
		"""
		attrs = self._to_json_str(p_attributes)
		with self.conn.cursor() as cur:
			cur.callproc("ORA26AI.SP_AI_TASK", [p_task_name, attrs])
		self.conn.commit()

	def create_agent(self, p_agent_name, p_attributes):
		"""
		Drop/Create/Enable an AGENT via ORA26AI.SP_AI_AGENT.
		"""
		attrs = self._to_json_str(p_attributes)
		with self.conn.cursor() as cur:
			cur.callproc("ORA26AI.SP_AI_AGENT", [p_agent_name, attrs])
		self.conn.commit()

	def create_team(self, p_team_name, p_attributes):
		"""
		Drop/Create a TEAM via ORA26AI.SP_AI_TEAM.
		"""
		attrs = self._to_json_str(p_attributes)
		with self.conn.cursor() as cur:
			cur.callproc("ORA26AI.SP_AI_TEAM", [p_team_name, attrs])
		self.conn.commit()

	def validate_name(self, p_object_type: str, p_object_name: str):
		"""
		Validates uniqueness of an AI object name by type. Raises if name exists.
		"""
		with self.conn.cursor() as cur:
			cur.callproc("ORA26AI.SP_AI_NAME_VALIDATE", [p_object_type, p_object_name])
		self.conn.commit()

	def list_functions_and_procedures(self, owner: str):
		"""
		# Lists standalone functions and procedures in the specified schema.
		# Returns a DataFrame with columns: owner, routine_name, routine_type, status.
		"""
		query = """
			SELECT
				ao.owner AS OWNER,
				ao.object_name AS NAME,
				ao.object_type AS TYPE,
				ao.status AS STATUS
			FROM all_objects ao
			WHERE ao.owner = UPPER(:p_owner)
			  AND ao.object_type IN ('FUNCTION','PROCEDURE')
		"""
		return pd.read_sql(query, con=self.conn, params={"p_owner": owner})