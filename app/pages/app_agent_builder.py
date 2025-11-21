# app_agent_builder.py (versión simplificada y alineada)
import os, json, random
from uuid import uuid4
from datetime import datetime
import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout

import components as component
import services.database as database
import services as service

# Initialize services
dbms_ai_agent_service = service.DBMSAIAgentService()
db_ai_agent_service   = database.DBMSAIAgentService()
select_ai_service     = service.SelectAIService()
select_ai_rag_service = service.SelectAIRAGService()

from dotenv import load_dotenv
load_dotenv()

# Load login and footer components
st.session_state["page"] = "app_agent_builder.py"
login = component.get_login()
component.get_footer()

st.set_page_config(
    page_title="Oracle AI Accelerator",
    page_icon="🅾️"
)

if login:
    st.set_page_config(layout="wide")
    
    user_id          = st.session_state["user_id"]
    profile_name_sql = select_ai_service.get_profile(user_id)
    profile_name_rag = select_ai_rag_service.get_profile(user_id)
    
    # Header y descripción
    st.header(":material/flowchart: Agent Builder")
    st.caption("DBMS_CLOUD_AI_AGENT: leverage the power of Autonomous Database to create, evaluate, and manage AI agents for advanced data-driven applications.")

    # --- helpers de presentación (etiquetas y colores) ---
    TYPE_ICON = {
        'AGENT': '🟦',
        'TASK': '🟩',
        'TOOL': '🔶',
        'EDGE': '🟪',
        'TEAM': '🔴',
        'DEFAULT': '⬜',
    }
    TYPE_COLOR = {
        'AGENT': '#1f77b4',   # azul
        'TASK': '#2ca02c',    # verde
        'TOOL': '#ff7f0e',    # naranja
        'EDGE': '#9467bd',    # púrpura
        'TEAM': '#ff0000',    # rojo
        'DEFAULT': '#cccccc', # gris
    }
    
    # --- generación de scripts DBMS_CLOUD_AI_AGENT ---
    _OBJECT_PARAM_MAP = {
        'TOOL': 'tool_name',
        'TASK': 'task_name',
        'AGENT': 'agent_name',
        'TEAM': 'team_name',
    }

    def _to_bool_literal(value) -> str:
        return "True" if str(value).strip().lower() in {"true", "1", "yes", "y"} else "False"

    def _indent_json_block(json_text: str, spaces: int = 12) -> str:
        padding = " " * spaces
        return "\n".join(f"{padding}{line}" for line in json_text.splitlines())

    def _build_dbms_block(object_type: str, identifier: str, attributes: dict | None) -> str:
        if not identifier:
            return ""
        attributes = attributes or {}
        json_text = json.dumps(attributes, indent=4, ensure_ascii=False)
        # Escape single quotes to embed safely into PL/SQL string literal
        json_text = json_text.replace("'", "''")
        attr_block = _indent_json_block(json_text)
        param = _OBJECT_PARAM_MAP.get(object_type.upper())
        if not param:
            return ""
        return (
            f"BEGIN\n"
            f"    DBMS_CLOUD_AI_AGENT.DROP_{object_type}({param} => '{identifier}', force => TRUE);\n\n"
            f"    DBMS_CLOUD_AI_AGENT.CREATE_{object_type}(\n"
            f"        {param} => '{identifier}',\n"
            f"        attributes => '\n"
            f"{attr_block}\n"
            f"        ');\n"
            f"END;\n"
            f"/"
        )

    def _build_tool_attributes(data: dict) -> dict:
        attrs = {
            "tool_type": data.get('tool_type_attr', 'SQL')
        }
        if data.get('instruction_attr'):
            attrs["instruction"] = data.get('instruction_attr')
        if attrs["tool_type"] == 'CUSTOM':
            if data.get('function_attr'):
                attrs["function"] = data.get('function_attr')
        else:
            profile_name = data.get('tool_profile_name_attr') or data.get('profile_name_attr')
            if profile_name:
                attrs["tool_params"] = {"profile_name": profile_name}
        if data.get('description'):
            attrs["description"] = data.get('description')
        return attrs

    def _parse_generic_list(value) -> list[str]:
        if isinstance(value, str):
            return [t.strip() for t in value.split(",") if t.strip()]
        if isinstance(value, (list, tuple, set)):
            return [str(t).strip() for t in value if str(t).strip()]
        return []

    def _parse_tools(value) -> list[str]:
        return _parse_generic_list(value)

    def _parse_task_inputs(value) -> list[str]:
        return _parse_generic_list(value)

    def _build_task_attributes(data: dict) -> dict:
        attrs = {
            "instruction": data.get('instruction_attr', '')
        }
        tools = _parse_tools(data.get('tools_attr'))
        if tools:
            attrs["tools"] = tools
        inputs = _parse_task_inputs(data.get('input_attr'))
        if inputs:
            attrs["input"] = inputs[0] if len(inputs) == 1 else inputs
        if data.get('enable_human_tool') is not None:
            attrs["enable_human_tool"] = _to_bool_literal(data.get('enable_human_tool'))
        if data.get('description'):
            attrs["description"] = data.get('description')
        return attrs

    def _build_agent_attributes(data: dict) -> dict:
        attrs = {
            "profile_name": data.get('profile_name_attr') or data.get('profile', profile_name_sql),
            "role": data.get('role_attr', '')
        }
        attrs["enable_human_tool"] = _to_bool_literal(data.get('enable_human_tool_attr', 'false'))
        if data.get('description'):
            attrs["description"] = data.get('description')
        return attrs

    def _normalize_team_agents(raw_value) -> list[dict]:
        items: list[dict] = []
        if not raw_value:
            return items
        if isinstance(raw_value, str):
            try:
                parsed = json.loads(raw_value)
            except Exception:
                parsed = []
        else:
            parsed = raw_value
        for entry in list(parsed if isinstance(parsed, (list, tuple)) else []):
            if isinstance(entry, dict):
                name = entry.get('agent') or entry.get('name')
                task = entry.get('task')
                if name and task:
                    items.append({"name": name, "task": task})
            elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
                name, task = entry[0], entry[1]
                if name and task:
                    items.append({"name": name, "task": task})
        return items

    def _build_team_attributes(agents_map: list[dict]) -> dict:
        return {
            "agents": [
                {"name": a.get('name'), "task": a.get('task')}
                for a in agents_map
                if isinstance(a, dict) and a.get('name') and a.get('task')
            ],
            "process": "sequential"
        }

    def generate_object_scripts(flow_state: StreamlitFlowState) -> list[dict]:
        scripts: list[dict] = []
        nodes = list(getattr(flow_state, "nodes", []) or [])
        edges = list(getattr(flow_state, "edges", []) or [])
        team_scripts_created: set[str] = set()
        for node in nodes:
            data = node.data or {}
            ntype = str(data.get('type', '')).upper()
            if ntype == 'TOOL':
                tool_name = data.get('tool_name') or data.get('name')
                attrs = _build_tool_attributes(data)
                script_text = _build_dbms_block('TOOL', tool_name, attrs)
                if script_text:
                    scripts.append({"label": f"CREATE TOOL · {tool_name}", "script": script_text})
            elif ntype == 'TASK':
                task_name = data.get('task_name') or data.get('name')
                attrs = _build_task_attributes(data)
                script_text = _build_dbms_block('TASK', task_name, attrs)
                if script_text:
                    scripts.append({"label": f"CREATE TASK · {task_name}", "script": script_text})
            elif ntype == 'AGENT':
                agent_name = data.get('agent_name') or data.get('name')
                attrs = _build_agent_attributes(data)
                script_text = _build_dbms_block('AGENT', agent_name, attrs)
                if script_text:
                    scripts.append({"label": f"CREATE AGENT · {agent_name}", "script": script_text})
            elif ntype == 'TEAM':
                team_name = data.get('team_name') or data.get('name')
                raw_agents = data.get('team_assignments') or data.get('agents_attr')
                normalized_agents = _normalize_team_agents(raw_agents)
                if team_name and normalized_agents:
                    attrs = _build_team_attributes(normalized_agents)
                    script_text = _build_dbms_block('TEAM', team_name, attrs)
                    if script_text:
                        scripts.append({"label": f"CREATE TEAM · {team_name}", "script": script_text})
                        team_scripts_created.add(team_name)
        # Construir script de TEAM basado en edges (AGENT -> TASK)
        agents_map = []
        nodes_by_id = {n.id: n for n in nodes}
        for e in edges:
            source = nodes_by_id.get(e.source)
            target = nodes_by_id.get(e.target)
            if not source or not target:
                continue
            source_type = str(((source.data or {}).get('type', ''))).upper()
            target_type = str(((target.data or {}).get('type', ''))).upper()
            if source_type == 'AGENT' and target_type == 'TASK':
                agents_map.append({
                    "name": (source.data or {}).get('agent_name') or (source.data or {}).get('name'),
                    "task": (target.data or {}).get('task_name') or (target.data or {}).get('name')
                })
        clean_agents = [a for a in agents_map if a.get('name') and a.get('task')]
        if clean_agents and not team_scripts_created:
            team_name = "TEAM_STREAMLIT_FLOW"
            team_attrs = _build_team_attributes(clean_agents)
            script_text = _build_dbms_block('TEAM', team_name, team_attrs)
            if script_text:
                scripts.append({"label": f"TEAM · {team_name}", "script": script_text})
        return scripts

    def build_node_content(node_data: dict) -> str:
        ntype = (node_data or {}).get('type', 'DEFAULT')
        name = (node_data or {}).get('name', '')
        icon = TYPE_ICON.get(str(ntype).upper(), TYPE_ICON['DEFAULT'])
        label_type = str(ntype).upper()
        return f"{icon} {label_type} <br/> {name}"
    
    def apply_node_visuals(node: StreamlitFlowNode) -> None:
        data = node.data or {}
        ntype = data.get('type')
        
        # Content
        if not data.get('content'):
            data['content'] = build_node_content({'type': ntype, 'name': data.get('name', node.id)})
        node.data = data

        # Style
        color = TYPE_COLOR.get(ntype, TYPE_COLOR['DEFAULT'])
        node.style = {
            'borderColor': color,
            'borderWidth': 2,
            'borderStyle': 'solid',
            'borderRadius': 8,
            'font-size': '8px',
        }

        # Habilitar capacidades
        node.draggable = True
        node.connectable = True
        node.deletable = True
        # Opcional: permitir selección explícita si el lib lo usa
        node.selectable = True

    def add_agent_builder_node(node_type: str) -> None:
        ntype = (node_type or '').upper()
        if not ntype or 'ai-agent' not in st.session_state:
            return

        node_id = f"{ntype}_{uuid4().hex[:6]}"
        base_data = {
            'type': ntype,
            'name': node_id,
            'content': build_node_content({'type': ntype, 'name': node_id})
        }

        if ntype == 'TOOL':
            new_node = StreamlitFlowNode(
                id=node_id,
                pos=(0, 1),
                data=base_data,
                node_type='output',
                source_position='top'
            )
        elif ntype == 'TASK':
            new_node = StreamlitFlowNode(
                id=node_id,
                pos=(1, 1),
                data=base_data,
                node_type='default',
                source_position='bottom',
                target_position='top'
            )
        elif ntype == 'AGENT':
            new_node = StreamlitFlowNode(
                id=node_id,
                pos=(0, -1),
                data=base_data,
                node_type='output',
                source_position='top'
            )
        elif ntype == 'TEAM':
            new_node = StreamlitFlowNode(
                id=node_id,
                pos=(0, -1),
                data=base_data,
                node_type='input',
                source_position='bottom'
            )
        else:
            return

        apply_node_visuals(new_node)
        st.session_state['ai-agent'].nodes.append(new_node)
    
    # --- inicialización de estado del grafo ---
    if 'ai-agent' not in st.session_state or st.session_state['ai-agent'] is None:
        st.session_state['ai-agent'] = StreamlitFlowState([], [])
    if getattr(st.session_state['ai-agent'], "nodes", None) is None:
        st.session_state['ai-agent'].nodes = []
    if getattr(st.session_state['ai-agent'], "edges", None) is None:
        st.session_state['ai-agent'].edges = []
    if not hasattr(st.session_state['ai-agent'], "selected_id"):
        st.session_state['ai-agent'].selected_id = None
    
    pending_action = st.session_state.pop('agent_builder_pending_action', None)
    if pending_action:
        add_agent_builder_node(pending_action.get('type'))
    
    # Ensure all existing nodes keep their visuals enabled (e.g. after editing)
    for n in st.session_state['ai-agent'].nodes:
        apply_node_visuals(n)

    tab1, tab2 = st.tabs(["Agent Flow", "Select AI Agents"])
    
    with tab1:
        st.session_state['ai-agent'] = streamlit_flow(
            'agent_flow',
            st.session_state['ai-agent'],
            layout=TreeLayout(direction='down'),
            fit_view=True,
            height=570,
            enable_node_menu=False,
            enable_edge_menu=True,
            enable_pane_menu=False,
            get_node_on_click=True,
            get_edge_on_click=True,
            allow_new_edges=True,
            show_minimap=True,
            hide_watermark=True,
            min_zoom=1
        )

    scripts_for_tab = generate_object_scripts(st.session_state['ai-agent'])

    with tab2:
        if scripts_for_tab:
            for idx, item in enumerate(scripts_for_tab, start=1):
                st.markdown(f"**{idx}. {item['label']}**")
                st.markdown(f"```sql\n{item['script']}\n```")
        else:
            st.info("Add tools, tasks, or agents to the flow to generate ready-to-execute scripts.")
    
    # -------- diálogos por tipo ----------
    sel = st.session_state['ai-agent'].selected_id

    @st.dialog("🔶 TOOL")
    def show_tool_dialog():
        
        # Get the selected node
        selected_id = st.session_state['ai-agent'].selected_id        
        node = next((n for n in st.session_state['ai-agent'].nodes if n.id == selected_id), None)
        data = node.data or {}
        
        # Show the caption
        st.caption(f"Use the `DBMS_CLOUD_AI_AGENT.CREATE_TOOL` procedure to register a custom tool that an agent can use during task processing. Each tool is identified by a unique tool_name and includes attributes that define its purpose, implementation logic, and metadata.")
        
        # Show the tool name
        data['tool_name'] = st.text_input(
            "Tool Name",
            key=f"tool_name_{node.id}",
            value=data.get('tool_name'),
            max_chars=100,
            help="A unique name to identify the tool."
        )
        data['name'] = data['tool_name']

        # Show the description
        data['description'] = st.text_area(
            "Description",
            key=f"tool_description_{node.id}",
            value=data.get('description'),
            max_chars=100,
            help="User-defined description to help identify the tool. This value is stored in the database but not sent to the LLM."
        )
        
        # Show the tool name
        data['instruction_attr'] = st.text_area(
            "Instruction `(attr)`",
            key=f"tool_instruction_attr_{node.id}",
            value=data.get('instruction_attr'),
            max_chars=250,
            help="A clear, concise statement that describes what the tool should accomplish and how to do it. This text is included in the prompt sent to the LLM."
        )
        
        # Show the tool type
        _tool_types = ['SQL','RAG','CUSTOM']
        _selected_tool_type = st.selectbox(
            "Tool Type `(attr)`",
            key=f"tool_type_attr_{node.id}",
            options=_tool_types,
            index=_tool_types.index(data.get('tool_type_attr')) if data.get('tool_type_attr') in _tool_types else 0,
            help="Specifies a built-in tool type. If set, instruction and function are not required."
        )
        data['tool_type_attr'] = _selected_tool_type
        
        # show the function if the tool type is CUSTOM
        if _selected_tool_type == 'CUSTOM':
            _owner = os.getenv('CON_ADB_DEV_USER_NAME') if user_id == 0 else f"SEL_AI_USER_ID_{user_id}"
            _df_function = db_ai_agent_service.list_functions_and_procedures(_owner)
            _selected_function = st.selectbox(
                "Function `(attr)`",
                key=f"function_attr_{node.id}",
                options=_df_function['NAME'],
                index=next((i for i, v in enumerate(_df_function['NAME']) if v == data.get('function_attr')), 0),
                format_func=lambda NAME: f"{_df_function.loc[_df_function['NAME'] == NAME, 'OWNER'].squeeze()}.{NAME} ({_df_function.loc[_df_function['NAME'] == NAME, 'TYPE'].squeeze()})",
                help="Specifies the PL/SQL procedure or function to call when the tool is used. This is a mandatory parameter for custom tools."
            )
            data['function_attr'] = _selected_function
        else:
            
            # Show the tool name
            if _selected_tool_type == 'SQL':
                _profile_name = profile_name_sql
            elif _selected_tool_type == 'RAG':
                _profile_name = profile_name_rag
            else:
                _profile_name = ""
            
            # Synchronize the value programmatically when the tool type changes
            st.session_state['profile_name_attr'] = _profile_name
            
            # Show the profile name
            data['profile_name_attr'] = st.text_input(
                "Profile Name `(attr)`",
                key=f"profile_name_attr_{node.id}",
                value=st.session_state.get('profile_name_attr', _profile_name),
                help="The profile name to use for the tool.",
                disabled=True
            )
            
            # Keep aligned with the attribute used by Run (tool_profile_name_attr)
            data['tool_profile_name_attr'] = data.get('profile_name_attr', _profile_name)

            # Build the node content
            data['content'] = build_node_content({'type':'TOOL','name':data.get('name', node.id)})

        # Show the buttons
        b1, b2 = st.columns(2)
        
        save_btn = False
        pressed_save = False
        has_assignments = bool(data.get('team_assignments'))

        with b1:
            # Save the tool
            pressed_save = st.button(":material/save: Save", type="secondary", width="stretch")
            if pressed_save:
                # Validación: function_attr solo requerido cuando el tipo es CUSTOM
                base_ok = bool(
                    data.get('tool_name') and
                    data.get('description') and
                    data.get('instruction_attr')
                )
                custom_ok = bool(data.get('function_attr')) if _selected_tool_type == 'CUSTOM' else True
                save_btn = bool(base_ok and custom_ok)
                    
        with b2:
            if st.button(":material/delete: Delete", key="delete_tool_btn", type="secondary", width="stretch"):
                if selected_id:
                    # Eliminar nodo y sus edges
                    st.session_state['ai-agent'].nodes = [
                        n for n in st.session_state['ai-agent'].nodes if n.id != selected_id
                    ]
                    st.session_state['ai-agent'].edges = [
                        e for e in st.session_state['ai-agent'].edges
                        if e.source != selected_id and e.target != selected_id
                    ]
                    st.session_state['ai-agent'].selected_id = None
                    st.rerun()
        
        if pressed_save:
            if save_btn:
                validate_name, msg = dbms_ai_agent_service.validate_name("TOOL", data['name'])
                if validate_name:                    
                    component.get_success(msg)
                    st.session_state['ai-agent'].selected_id = None
                    st.rerun()
                else:
                    component.get_error(msg)
            else:
                component.get_warning("Some required fields are missing. Please fill in all fields before saving.")

    @st.dialog("🟢 TASK")
    def show_task_dialog():
        
        # Get the selected node
        selected_id = st.session_state['ai-agent'].selected_id
        node = next((n for n in st.session_state['ai-agent'].nodes if n.id == selected_id), None)
        data = node.data or {}

        # Show the caption
        st.caption(f"Use the `DBMS_CLOUD_AI_AGENT.CREATE_TASK` procedure to define a task that a Select AI agent can include in its reasoning process. Each task has a unique name and a set of attributes that specify the agent's behavior when planning and performing the task.")
        
        # Show the task name
        data['task_name'] = st.text_input(
            "Task Name",
            key=f"task_name_{node.id}",
            value=data.get('task_name'),
            max_chars=20,
            help="A unique name for the task."
        )
        data['name'] = data['task_name']

        # Show the description
        data['description'] = st.text_area(
            "Description",
            key=f"task_description_{node.id}",
            value=data.get('description'),
            max_chars=100,
            help="User-defined description to help identify the task. This value is stored in the database but not sent to the LLM."
        )

        data['enable_human_tool'] = st.checkbox(
            "Enable Human Tool",
            key=f"enable_human_tool_{node.id}",
            value=data.get('enable_human_tool', 'true'),
            help="Enable agent to ask questions to user when it requires information or clarification during a task."
        )

        # Show the tool name
        data['instruction_attr'] = st.text_area(
            "Instruction `(attr)`",
            key=f"task_instruction_attr_{node.id}",
            value=data.get('instruction_attr'),
            max_chars=250,
            help="A clear, concise statement that describes what the task should accomplish. You can include a {query} placeholder to represent the user question."
        )

        # Detectar TOOLS conectados a esta TASK (soporta TASK->TOOL y TOOL->TASK)
        task_id = node.id
        edges = list(st.session_state['ai-agent'].edges or [])
        nodes_by_id = {n.id: n for n in st.session_state['ai-agent'].nodes}
        connected_tool_names = []
        
        # Get the connected tools
        for e in edges:
            # Caso 1: TASK -> TOOL
            if e.source == task_id:
                target_node = nodes_by_id.get(e.target)
                if target_node and str(((target_node.data or {}).get('type',''))).upper() == 'TOOL':
                    td = target_node.data or {}
                    connected_tool_names.append(td.get('name') or td.get('tool_name') or target_node.id)
            # Caso 2: TOOL -> TASK
            elif e.target == task_id:
                source_node = nodes_by_id.get(e.source)
                if source_node and str(((source_node.data or {}).get('type',''))).upper() == 'TOOL':
                    sd = source_node.data or {}
                    connected_tool_names.append(sd.get('name') or sd.get('tool_name') or source_node.id)
        # Normalizar lista única y ordenada
        connected_tool_names = sorted(list({t for t in connected_tool_names if str(t).strip()}))

        tools_csv = ",".join(connected_tool_names)
        data['tools_attr'] = tools_csv
        st.text_input(
            "Tools `(attr)`",
            key=f"task_tools_attr_{node.id}",
            value=tools_csv,
            help="A JSON array of tool names that the agent can use to complete the task. For example: 'tools': ['RAG', 'SQL', 'WEBSEARCH', 'NOTIFICATION'].",
            disabled=True
        )

        connected_task_names = []
        for e in edges:
            if e.target == task_id:
                source_node = nodes_by_id.get(e.source)
                if source_node and str(((source_node.data or {}).get('type',''))).upper() == 'TASK':
                    sd = source_node.data or {}
                    connected_task_names.append(sd.get('task_name') or sd.get('name') or source_node.id)
            elif e.source == task_id:
                target_node = nodes_by_id.get(e.target)
                if target_node and str(((target_node.data or {}).get('type',''))).upper() == 'TASK':
                    td = target_node.data or {}
                    connected_task_names.append(td.get('task_name') or td.get('name') or target_node.id)
        connected_task_names = sorted(list({t for t in connected_task_names if str(t).strip()}))
        input_csv = ",".join(connected_task_names)
        data['input_attr'] = input_csv
        if connected_task_names:
            st.text_input(
                "Input `(attr · optional)`",
                key=f"task_input_attr_{node.id}",
                value=input_csv,
                help="Specifies the task names that feed their output into this task. Optional field.",
                disabled=True
            )
        else:
            st.caption("Input `(attr · optional)`")
            st.info("Connect this task with other task nodes to populate this optional field automatically.")
        
        data['content'] = build_node_content({'type':'TASK','name':data.get('name', node.id)})
        
        # Show the buttons
        b1, b2 = st.columns(2)
        
        save_btn = False
        pressed_save = False

        placeholder_missing = False

        with b1:
            # Save the tool
            pressed_save = st.button(":material/save: Save", type="secondary", width="stretch")
            if pressed_save:
                instruction_text = data.get('instruction_attr', '')
                has_placeholder = any(token in instruction_text for token in ("{query}", "{QUERY}", "{Query}"))
                placeholder_missing = not has_placeholder
                base_ok = bool(
                    data.get('task_name') and
                    data.get('description') and
                    instruction_text and
                    data.get('tools_attr') and
                    has_placeholder
                )
                save_btn = bool(base_ok)
                    
        with b2:
            if st.button(":material/delete: Delete", key="delete_tool_btn", type="secondary", width="stretch"):
                if selected_id:
                    # Eliminar nodo y sus edges
                    st.session_state['ai-agent'].nodes = [
                        n for n in st.session_state['ai-agent'].nodes if n.id != selected_id
                    ]
                    st.session_state['ai-agent'].edges = [
                        e for e in st.session_state['ai-agent'].edges
                        if e.source != selected_id and e.target != selected_id
                    ]
                    st.session_state['ai-agent'].selected_id = None
                    st.rerun()
        
        if pressed_save:
            if save_btn:
                validate_name, msg = dbms_ai_agent_service.validate_name("TASK", data['name'])
                if validate_name:                    
                    component.get_success(msg)
                    st.session_state['ai-agent'].selected_id = None
                    st.rerun()
                else:
                    component.get_error(msg)
            else:
                if placeholder_missing:
                    component.get_warning("Instruction `(attr)` must include the {query} placeholder.")
                else:
                    component.get_warning("Some required fields are missing. Please fill in all fields before saving.")

    @st.dialog("🟦 AGENT")
    def show_agent_dialog():
        
        # Get the selected node
        selected_id = st.session_state['ai-agent'].selected_id
        node = next((n for n in st.session_state['ai-agent'].nodes if n.id == selected_id), None)
        data = node.data or {}
        
        # Show the caption
        st.caption(f"Use the `DBMS_CLOUD_AI_AGENT.CREATE_AGENT` procedure to register a new AI agent in the Select AI Agent framework. Define the agent’s identity using agent_name, configure its behavior with the attributes parameter, and optionally provide a description.")
        
        # Show the tool name
        data['agent_name'] = st.text_input(
            "Agent Name",
            key=f"agent_name_{node.id}",
            value=data.get('agent_name'),
            max_chars=100,
            help="A name for the AI agent. The agent name must follow the naming rules of Oracle SQL identifier. Maximum length of name is 125 characters."
        )
        data['name'] = data['agent_name']

        # Show the description
        data['description'] = st.text_area(
            "Description",
            key=f"agent_description_{node.id}",
            value=data.get('description'),
            max_chars=100,
            help="User-specified description for the AI agent."
        )

        # Show the tool name
        data['role_attr'] = st.text_area(
            "Role `(attr)`",
            key=f"role_attr_{node.id}",
            value=data.get('role_attr'),
            max_chars=250,
            help="Define the agent's function and provide context to the agent. This is sent to LLM."
        )

        data['enable_human_tool_attr'] = st.checkbox(
            "Enable Human Tool `(attr)`",
            key=f"enable_human_tool_attr_{node.id}",
            value=data.get('enable_human_tool', 'true'),
            help="Enable agent to ask questions to the user for information or clarification."
        )

        # Show the profile name
        _profile_name = profile_name_sql
        data['profile_name_attr'] = st.text_input(
            "Profile Name `(attr)`",
            key=f"profile_name_attr_{node.id}",
            value=st.session_state.get('profile_name_attr', _profile_name),
            help="The AI profile that the agent is using to send request to LLM.",
            disabled=True
        )

        data['content'] = build_node_content({'type':'AGENT','name':data.get('name', node.id)})

        # Show the buttons
        b1, b2 = st.columns(2)
        
        save_btn = False
        pressed_save = False

        with b1:
            # Save the tool
            pressed_save = st.button(":material/save: Save", type="secondary", width="stretch")
            if pressed_save:
                # Validación: function_attr solo requerido cuando el tipo es CUSTOM
                base_ok = bool(
                    data.get('agent_name') and
                    data.get('description') and
                    data.get('role_attr')
                )
                save_btn = bool(base_ok)
                    
        with b2:
            if st.button(":material/delete: Delete", key="delete_tool_btn", type="secondary", width="stretch"):
                if selected_id:
                    # Eliminar nodo y sus edges
                    st.session_state['ai-agent'].nodes = [
                        n for n in st.session_state['ai-agent'].nodes if n.id != selected_id
                    ]
                    st.session_state['ai-agent'].edges = [
                        e for e in st.session_state['ai-agent'].edges
                        if e.source != selected_id and e.target != selected_id
                    ]
                    st.session_state['ai-agent'].selected_id = None
                    st.rerun()
        
        if pressed_save:
            if save_btn:
                validate_name, msg = dbms_ai_agent_service.validate_name("AGENT", data['name'])
                if validate_name:                    
                    component.get_success(msg)
                    st.session_state['ai-agent'].selected_id = None
                    st.rerun()
                else:
                    component.get_error(msg)
            else:
                component.get_warning("Some required fields are missing. Please fill in all fields before saving.")
    
    @st.dialog("🟪 EDGE")
    def show_edge_dialog():
        
        # Get the selected edge
        selected_id = st.session_state['ai-agent'].selected_id
        edge = next((e for e in st.session_state['ai-agent'].edges if e.id == selected_id), None)
        
        # Show the caption
        st.caption(f"""
            - `TOOL → TASK`: The TASK can use this TOOL; it is added to tools_attr (CREATE_TASK Attributes).
            - `TASK → TASK`: Defines precedence/calls between tasks; the order is respected when orchestrating (TEAM process 'sequential').
            - `AGENT → TASK`: Assigns the TASK to the AGENT; this is used to build "agents" when creating the TEAM (CREATE_TEAM Attributes).
        """)
        
        # Show friendly names (tool_name/name) instead of IDs
        nodes_by_id = {n.id: n for n in st.session_state['ai-agent'].nodes}
        def _node_display_name(node):
            if not node:
                return "?"
            d = node.data or {}
            ntype = str(d.get('type','')).upper()
            if ntype == 'TOOL':
                return d.get('tool_name') or d.get('name') or node.id
            return d.get('name') or node.id
        source_node = nodes_by_id.get(edge.source)
        target_node = nodes_by_id.get(edge.target)
        
        # Show flow direction: target_node ← source_node
        st.write(f"{edge.source} ({_node_display_name(source_node)}) ← {edge.target} ({_node_display_name(target_node)})")
        
        if st.button(":material/delete: Delete", key="delete_edge_btn", type="secondary"):
            if selected_id:
                st.session_state['ai-agent'].edges = [
                    e for e in st.session_state['ai-agent'].edges if e.id != selected_id
                ]
                st.session_state['ai-agent'].selected_id = None
                st.rerun()

    @st.dialog("🔴 TEAM")
    def show_team_dialog():
        
        # Get the selected node
        selected_id = st.session_state['ai-agent'].selected_id
        node = next((n for n in st.session_state['ai-agent'].nodes if n.id == selected_id), None)
        data = node.data or {}

        # Show the caption
        st.caption(f"Use the `DBMS_CLOUD_AI_AGENT.CREATE_TEAM` procedure to define a team of agents that will work together to complete a task. Each team has a unique name and a set of attributes that specify the agents' behavior when planning and performing the task.")
        
        # Show the team name
        data['team_name'] = st.text_input(
            "Team Name",
            key=f"team_name_{node.id}",
            value=data.get('team_name'),
            max_chars=100,
            help="A unique name to identify the AI agent team."
        )
        data['name'] = data['team_name']

        # Show the description
        data['description'] = st.text_area(
            "Description",
            key=f"team_description_{node.id}",
            value=data.get('description'),
            max_chars=100,
            help="User-defined description to identify the team's purpose. This value is stored in the database but not sent to the LLM."
        )

        # Build selectable lists from existing nodes
        nodes_catalog = list(st.session_state['ai-agent'].nodes or [])
        agent_options = sorted(list({
            (n.data or {}).get('agent_name') or (n.data or {}).get('name') or n.id
            for n in nodes_catalog
            if str(((n.data or {}).get('type',''))).upper() == 'AGENT'
        }))
        task_options = sorted(list({
            (n.data or {}).get('task_name') or (n.data or {}).get('name') or n.id
            for n in nodes_catalog
            if str(((n.data or {}).get('type',''))).upper() == 'TASK'
        }))

        # Persist assignments list
        assignments = list(data.get('team_assignments') or [])
        data['team_assignments'] = assignments
        data['agents_attr'] = json.dumps(assignments, ensure_ascii=False) if assignments else ""
        has_assignments = bool(assignments)

        col_agent, col_task = st.columns(2)
        with col_agent:
            agent_select_options = agent_options if agent_options else ["No agents available"]
            selected_agent = st.selectbox(
                "Agent Name `(attr)`",
                options=agent_select_options,
                key=f"team_agent_select_{node.id}",
                disabled=not agent_options,
                help="Select one of the defined agents."
            )
            if not agent_options:
                selected_agent = None
        with col_task:
            task_select_options = task_options if task_options else ["No tasks available"]
            selected_task = st.selectbox(
                "Task Name `(attr)`",
                options=task_select_options,
                key=f"team_task_select_{node.id}",
                disabled=not task_options,
                help="Select the task to be assigned to the agent."
            )
            if not task_options:
                selected_task = None
        action_col_add, action_col_clear = st.columns(2)
        add_disabled = not (agent_options and task_options)
        with action_col_add:
            if st.button("Add Agents `(attr)`", key=f"team_add_assignment_{node.id}", type="secondary", disabled=add_disabled, use_container_width=True):
                if selected_agent and selected_task:
                    if not any(a.get('agent') == selected_agent and a.get('task') == selected_task for a in assignments):
                        assignments.append({'agent': selected_agent, 'task': selected_task})
                        data['team_assignments'] = assignments
                        data['agents_attr'] = json.dumps(assignments, ensure_ascii=False)
                        node.data = data
        with action_col_clear:
            clear_disabled = not assignments
            if st.button("Clear Agents `(attr)`", key=f"team_clear_assignment_{node.id}", type="secondary", disabled=clear_disabled, use_container_width=True):
                assignments.clear()
                data['team_assignments'] = assignments
                data['agents_attr'] = ""
                node.data = data

        st.markdown("Agents `(attr)`")
        if assignments:
            st.code(json.dumps(assignments, indent=2, ensure_ascii=False), language="json")
        else:
            st.warning("There are no agents assigned yet. Select an agent and a task, then click Add.")

        has_assignments = bool(assignments)

        data['content'] = build_node_content({'type':'TEAM','name':data.get('name', node.id)})
        
        # Show the buttons
        b1, b2 = st.columns(2)
        
        save_btn = False
        pressed_save = False

        with b1:
            # Save the team
            pressed_save = st.button(":material/save: Save", type="secondary", width="stretch")
            if pressed_save:
                base_ok = bool(
                    data.get('team_name') and
                    data.get('description') and
                    has_assignments
                )
                save_btn = bool(base_ok)
                    
        with b2:
            if st.button(":material/delete: Delete", key="delete_team_btn", type="secondary", width="stretch"):
                if selected_id:
                    # Eliminar nodo y sus edges
                    st.session_state['ai-agent'].nodes = [
                        n for n in st.session_state['ai-agent'].nodes if n.id != selected_id
                    ]
                    st.session_state['ai-agent'].edges = [
                        e for e in st.session_state['ai-agent'].edges
                        if e.source != selected_id and e.target != selected_id
                    ]
                    st.session_state['ai-agent'].selected_id = None
                    st.rerun()
        
        if pressed_save:
            if save_btn:
                validate_name, msg = dbms_ai_agent_service.validate_name("TEAM", data['name'])
                if validate_name:                    
                    component.get_success(msg)
                    st.session_state['ai-agent'].selected_id = None
                    st.rerun()
                else:
                    component.get_error(msg)
            else:
                component.get_warning("Some required fields are missing. Please fill in all fields before saving.") 

    # Invoke the appropriate dialog based on the selection
    if sel:
        node = next((n for n in st.session_state['ai-agent'].nodes if n.id == sel), None)
        if node:
            ntype = str((node.data or {}).get('type','')).upper()
            if ntype == 'TOOL':
                show_tool_dialog()
            elif ntype == 'TASK':
                show_task_dialog()
            elif ntype == 'AGENT':
                show_agent_dialog()
            elif ntype == 'TEAM':
                show_team_dialog()
        else:
            edge = next((e for e in st.session_state['ai-agent'].edges if e.id == sel), None)
            if edge:
                show_edge_dialog()
