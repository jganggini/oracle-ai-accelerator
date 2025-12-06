    CREATE OR REPLACE PROCEDURE SP_AI_NAME_VALIDATE (
        p_object_type IN VARCHAR2,  /* TEAM, AGENT, TASK, TOOL */
        p_object_name IN VARCHAR2
    ) AS
        v_cnt INTEGER := 0;
        v_type VARCHAR2(16) := UPPER(TRIM(p_object_type));
        v_name VARCHAR2(256) := TRIM(p_object_name);
    BEGIN
        IF v_type IS NULL OR v_name IS NULL THEN
            RAISE_APPLICATION_ERROR(-20001, 'Invalid arguments: object_type and object_name are required');
        END IF;

        /* TEAM */
        IF v_type = 'TEAM' THEN
            SELECT COUNT(*) INTO v_cnt
            FROM USER_AI_AGENT_TEAMS
            WHERE UPPER(AGENT_TEAM_NAME) = UPPER(v_name);

            IF v_cnt > 0 THEN
                RAISE_APPLICATION_ERROR(-20002, 'Name already exists for TEAM (code): ' || v_name);
            END IF;

            RETURN;
        END IF;
        
        /* AGENT */
        IF v_type = 'AGENT' THEN
            SELECT COUNT(*) INTO v_cnt
            FROM USER_AI_AGENTS
            WHERE UPPER(AGENT_NAME) = UPPER(v_name);

            IF v_cnt > 0 THEN
                RAISE_APPLICATION_ERROR(-20002, 'Name already exists for AGENT (code): ' || v_name);
            END IF;

            RETURN;
        END IF;
        
        /* TASK */
        IF v_type = 'TASK' THEN
            SELECT COUNT(*) INTO v_cnt
            FROM USER_AI_AGENT_TASKS
            WHERE UPPER(TASK_NAME) = UPPER(v_name);

            IF v_cnt > 0 THEN
                RAISE_APPLICATION_ERROR(-20002, 'Name already exists for TASK (code): ' || v_name);
            END IF;

            RETURN;
        END IF;

        /* TOOL */
        IF v_type = 'TOOL' THEN
            SELECT COUNT(*) INTO v_cnt
            FROM USER_AI_AGENT_TOOLS
            WHERE UPPER(TOOL_NAME) = UPPER(v_name);

            IF v_cnt > 0 THEN
                RAISE_APPLICATION_ERROR(-20002, 'Name already exists for TOOL (code): ' || v_name);
            END IF;

            RETURN;
        END IF; 
        
        RAISE_APPLICATION_ERROR(-20005, 'Unsupported object_type: ' || v_type);
    END;
    /
    --