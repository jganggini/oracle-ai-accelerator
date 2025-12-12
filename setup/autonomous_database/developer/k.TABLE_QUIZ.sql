    CREATE TABLE quiz (
        quiz_id           NUMBER NOT NULL,
        file_id           NUMBER NOT NULL,
        question_id       NUMBER NOT NULL,
        module_id         NUMBER NOT NULL,
        module_name       VARCHAR2(250) NOT NULL,
        module_percentage NUMBER DEFAULT 0 NOT NULL,
        question_en       VARCHAR2(4000) NOT NULL,
        question_es       VARCHAR2(4000) NOT NULL,
        question_pt       VARCHAR2(4000) NOT NULL,
        options_en        CLOB CHECK (options_en IS JSON) NOT NULL,
        options_es        CLOB CHECK (options_es IS JSON) NOT NULL,
        options_pt        CLOB CHECK (options_pt IS JSON) NOT NULL,
        explanation_en    VARCHAR2(4000),
        explanation_es    VARCHAR2(4000),
        explanation_pt    VARCHAR2(4000),
        quiz_state        NUMBER DEFAULT 1 NOT NULL,
        quiz_date         TIMESTAMP(6) DEFAULT SYSDATE NOT NULL,
        CONSTRAINT pk_quiz_id     PRIMARY KEY (quiz_id),
        CONSTRAINT fk_quiz_files  FOREIGN KEY (file_id) REFERENCES files(file_id),
        CONSTRAINT fk_quiz_modules FOREIGN KEY (module_id) REFERENCES modules(module_id)
        ENABLE
    );
    --

    CREATE UNIQUE INDEX quiz_file_question_unq ON quiz (file_id, question_id);
    --

    CREATE INDEX idx_quiz_file_id ON quiz (file_id, quiz_state);
    --

    CREATE SEQUENCE quiz_id_seq START WITH 1 INCREMENT BY 1 NOCACHE;
    --

    CREATE OR REPLACE TRIGGER trg_quiz_id
        BEFORE INSERT ON quiz
        FOR EACH ROW
        WHEN (NEW.quiz_id IS NULL)
    BEGIN
        :NEW.quiz_id := quiz_id_seq.NEXTVAL;
    END;
    /
    --
