    CREATE OR REPLACE PROCEDURE SP_SEL_AI_AGENT (
        p_profile_name_sql IN VARCHAR2,
        p_profile_name_rag IN VARCHAR2
    )
    AS
        l_agent_name           VARCHAR2(255)  := p_profile_name_sql || '_AGENCY';
        l_task_name            VARCHAR2(255)  := p_profile_name_sql || '_TASK';
        l_tool_name_sql        VARCHAR2(255)  := p_profile_name_sql || '_SQL_TOOL';
        l_tool_name_rag        VARCHAR2(255)  := p_profile_name_rag || '_RAG_TOOL';
        l_team_name            VARCHAR2(255)  := p_profile_name_sql || '_TEAM';
    BEGIN
        /* 1) Drop the agent if it exists */
        DBMS_CLOUD_AI_AGENT.DROP_AGENT(agent_name => l_agent_name, force => TRUE);

        /* 2) Create the agent */
        DBMS_CLOUD_AI_AGENT.CREATE_AGENT(
            agent_name => l_agent_name,
            attributes => '{
                "profile_name": "' || p_profile_name_sql || '",
                "role": "You are an analyst who decides whether to respond using SQL, RAG, or both. First, plan your approach, then act, and finally explain briefly how you solved the query.",
                "enable_human_tool": "False"
                }');

        /* 3) Drop the task if it exists */
        DBMS_CLOUD_AI_AGENT.DROP_TASK(task_name => l_task_name, force => TRUE);

        /* 4) Create the task */
        DBMS_CLOUD_AI_AGENT.CREATE_TASK(
            task_name => l_task_name,
            attributes => '{
                "instruction": "Answer the user''s query {query}. If the question is about database data, use SQL_TOOL. If it requires document context, use RAG_TOOL. If it benefits from both, use both and concatenate the results.",
                "tools": ["' || l_tool_name_sql || '","' || l_tool_name_rag || '"]}'
        );

        /* 5) Drop the team if it exists */
        DBMS_CLOUD_AI_AGENT.DROP_TEAM(team_name => l_team_name, force => TRUE);

        /* 6) Create the team */       
        DBMS_CLOUD_AI_AGENT.CREATE_TEAM(
            team_name  => l_team_name,
            attributes => '{"agents": [{"name":"' || l_agent_name || '", "task" : "' || l_task_name || '"}],
                            "process": "sequential"}');
        
    END;
    /
    --