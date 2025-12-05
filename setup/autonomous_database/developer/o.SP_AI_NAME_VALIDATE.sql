    CREATE OR REPLACE FUNCTION SP_AI_NAME_VALIDATE (
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

        /* TEAM: validar código lógico y nombres publicados */
        IF v_type = 'TEAM' THEN
            SELECT COUNT(*) INTO v_cnt
            FROM ORA26AI.AI_TEAM
            WHERE UPPER(ai_team_code) = UPPER(v_name);

            IF v_cnt > 0 THEN
                RAISE_APPLICATION_ERROR(-20002, 'Name already exists for TEAM (code): ' || v_name);
            END IF;

            SELECT COUNT(*) INTO v_cnt
            FROM ORA26AI.AI_TEAM_PUBLISH
            WHERE UPPER(ai_team_publish_name) = UPPER(v_name);

            IF v_cnt > 0 THEN
                RAISE_APPLICATION_ERROR(-20003, 'Name already exists for TEAM (published): ' || v_name);
            END IF;

            RETURN;
        END IF;

        /* AGENT|TASK|TOOL: validar por título globalmente */
        IF v_type IN ('AGENT', 'TASK', 'TOOL') THEN
            SELECT COUNT(*) INTO v_cnt
            FROM ORA26AI.AI_NODE
            WHERE UPPER(ai_node_type) = v_type
            AND UPPER(ai_node_title) = UPPER(v_name);

            IF v_cnt > 0 THEN
                RAISE_APPLICATION_ERROR(-20004, 'Name already exists for ' || v_type || ': ' || v_name);
            END IF;

            RETURN;
        END IF;

        RAISE_APPLICATION_ERROR(-20005, 'Unsupported object_type: ' || v_type);
    END;
    /
    --