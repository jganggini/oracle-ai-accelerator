import json
from dotenv import load_dotenv
import components as component
import services.database as database

# Initialize the service
db_ai_agent_service = database.DBMSAIAgentService()

load_dotenv()

class DBMSAIAgentService:

	# ---------- Validación ----------
	@staticmethod
	def validate_name(object_type: str, object_name: str) -> bool:
		try:
			db_ai_agent_service.validate_name(object_type.upper(), object_name)
			message = f"[Agent AI] Name available for {object_type.upper()}: '{object_name}'."
			return True, message
		except Exception as e:
			message = f"[Error] {object_type.upper()} '{object_name}' already exists or is invalid."
			return False, message

	@staticmethod
	def _to_json(attributes) -> dict:
		if attributes is None:
			return {}
		if isinstance(attributes, str):
			try:
				return json.loads(attributes)
			except Exception:
				return {}
		return dict(attributes)

	# ---------- TOOL ----------
	@staticmethod
	def create_tool(
		name: str,
		tool_type_attr: str,
		instruction_attr: str | None = None,
		function_attr: str | None = None,
		profile_name_attr: str | None = None,
		schema_attr: str | None = None
	) -> None:
		"""
		Crea un TOOL usando campos individuales (_attr), alineado con la documentación.
		- tool_type_attr: 'SQL' | 'RAG' | 'CUSTOM'
		- instruction_attr/function_attr: para herramientas personalizadas
		- profile_name_attr/schema_attr/params_attr: parámetros adicionales (p.ej., SQL profile)
		"""

		attrs: dict = {"tool_type": tool_type_attr}
		if instruction_attr:
			attrs["instruction"] = instruction_attr
		if function_attr:
			attrs["function"] = function_attr
		if schema_attr:
			attrs["schema"] = schema_attr
		tool_params: dict = {}
		if profile_name_attr:
			tool_params["profile_name"] = profile_name_attr
		if tool_params:
			attrs["tool_params"] = tool_params
		try:
			db_ai_agent_service.create_tool(name, attrs)
			component.get_success(f"[Agent AI] Tool '{name}' has been created successfully.", ":material/build_circle:")
		except Exception as e:
			component.get_error(f"[Error] Agent AI - Create Tool:\n{e}")

	# ---------- TASK ----------
	@staticmethod
	def create_task(
		name: str,
		instruction_attr: str,
		tools_attr,
		extra: dict | None = None
	) -> None:
		"""
		instruction_attr: texto de la instrucción
		tools_attr: lista de nombres de tools (list[str]) o string CSV
		"""
		if isinstance(tools_attr, str):
			tools_list = [t.strip() for t in tools_attr.split(",") if t.strip()]
		else:
			tools_list = [str(t).strip() for t in list(tools_attr or []) if str(t).strip()]
		task_attrs = {
			"instruction": instruction_attr or "",
			"tools": tools_list
		}
		if extra:
			task_attrs.update(extra)
		try:
			db_ai_agent_service.create_task(name, task_attrs)
			component.get_success(f"[Agent AI] Task '{name}' has been created successfully.", ":material/edit_note:")
		except Exception as e:
			component.get_error(f"[Error] Agent AI - Create Task:\n{e}")

	# ---------- AGENT ----------
	@staticmethod
	def create_agent(
		name: str,
		profile_name_attr: str,
		role_attr: str,
		enable_human_tool_attr: str = "false"
	) -> None:
		# Normalizar booleano como string "True"/"False" según ejemplos de DBMS_CLOUD_AI_AGENT
		_enable_str = "True" if str(enable_human_tool_attr).strip().lower() in {"true", "1", "yes", "y"} else "False"
		agent_attrs = {
			"profile_name": profile_name_attr,
			"role": role_attr,
			"enable_human_tool": _enable_str
		}
		try:
			db_ai_agent_service.create_agent(name, agent_attrs)
			component.get_success(f"[Agent AI] Agent '{name}' has been created successfully.", ":material/smart_toy:")
		except Exception as e:
			component.get_error(f"[Error] Agent AI - Create Agent:\n{e}")

	# ---------- TEAM ----------
	@staticmethod
	def create_team(
		team_name: str,
		agents_attr: list[dict],
		process_attr: str = "sequential"
	) -> None:
		"""
		agents: lista de objetos {'name': '<AGENT_NAME>', 'task': '<TASK_NAME>'}
		"""
		# Sanea la estructura de agents a lo requerido por DBMS_CLOUD_AI_AGENT
		clean_agents: list[dict] = []
		for a in list(agents_attr or []):
			try:
				_name = (a or {}).get("name")
				_task = (a or {}).get("task")
				if _name and _task:
					clean_agents.append({"name": _name, "task": _task})
			except Exception:
				continue
		team_attrs = {"agents": clean_agents, "process": (process_attr or "sequential")}
		try:
			db_ai_agent_service.create_team(team_name, team_attrs)
			component.get_success(f"[Team AI] Team '{team_name}' has been created successfully.", ":material/groups:")
		except Exception as e:
			component.get_error(f"[Error] Team AI - Create Team:\n{e}")
