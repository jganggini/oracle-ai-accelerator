    CREATE OR REPLACE FUNCTION SP_SEL_AI_AGENT_CONVERSATION (
        p_profile_name_sql IN VARCHAR2,
        p_query            IN VARCHAR2
    ) RETURN CLOB
    AS
        l_conversation_id      VARCHAR2(50);
        l_team_name            VARCHAR2(255)  := p_profile_name_sql || '_TEAM';
        l_final_answer         CLOB;
    BEGIN
        /* 1) Create the conversation */
        SELECT DBMS_CLOUD_AI.CREATE_CONVERSATION INTO l_conversation_id;

        /* 2) Run the team and capture the answer */
        l_final_answer := DBMS_CLOUD_AI_AGENT.RUN_TEAM(
            team_name   => l_team_name,
            user_prompt => p_query,
            params      => '{"conversation_id": "' || l_conversation_id || '"}'
        );
        
        RETURN l_final_answer;
    END;
    /
    --