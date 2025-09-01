    CREATE TABLE PROMPT_USER (
        prompt_user_id            NUMBER NOT NULL,
        prompt_id  NUMBER NOT NULL,
        user_id                  NUMBER NOT NULL,
        owner                    NUMBER DEFAULT 1 NOT NULL,    
        CONSTRAINT pk_prompt_user_id     PRIMARY KEY (prompt_user_id),
        CONSTRAINT fk_prompt_user_agents FOREIGN KEY (prompt_id) REFERENCES prompts(prompt_id),
        CONSTRAINT fk_prompt_user_users  FOREIGN KEY (user_id) REFERENCES users(user_id)
        ENABLE
    );
    --

    CREATE SEQUENCE prompt_user_id_seq START WITH 5 INCREMENT BY 1 NOCACHE

    --
    CREATE OR REPLACE TRIGGER trg_prompt_user_id
        BEFORE INSERT ON prompt_user
        FOR EACH ROW
        WHEN (NEW.prompt_user_id IS NULL)
    BEGIN
        :NEW.prompt_user_id := prompt_user_id_seq.NEXTVAL;
    END;
