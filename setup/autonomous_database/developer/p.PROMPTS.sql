    CREATE TABLE PROMPTS (
        prompt_id  NUMBER NOT NULL,
        prompt_name VARCHAR(40) NOT NULL,
        prompt_content VARCHAR2(4000) NOT NULL,
        CONSTRAINT pk_prompt_id     PRIMARY KEY (prompt_id)
    );
    --

    CREATE SEQUENCE prompt_id_seq START WITH 5 INCREMENT BY 1 NOCACHE

    --
    CREATE OR REPLACE TRIGGER trg_prompt_id
        BEFORE INSERT ON prompts
        FOR EACH ROW
        WHEN (NEW.prompt_id IS NULL)
    BEGIN
        :NEW.prompt_id := prompt_id_seq.NEXTVAL;
    END;
    /