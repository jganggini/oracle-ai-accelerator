    CREATE TABLE quiz_answers (
        quiz_answer_id       NUMBER NOT NULL,
        quiz_id              NUMBER NOT NULL,
        user_id              NUMBER NOT NULL,
        evaluation_name      VARCHAR2(500) NOT NULL,
        selected_option      NUMBER NOT NULL,
        is_correct           NUMBER NOT NULL,
        answer_time_seconds  NUMBER DEFAULT 0,
        quiz_answer_state    NUMBER DEFAULT 1 NOT NULL,
        quiz_answer_date     TIMESTAMP(6) DEFAULT SYSDATE NOT NULL,
        CONSTRAINT pk_quiz_answer_id     PRIMARY KEY (quiz_answer_id),
        CONSTRAINT fk_quiz_answer_quiz   FOREIGN KEY (quiz_id) REFERENCES quiz(quiz_id),
        CONSTRAINT fk_quiz_answer_user   FOREIGN KEY (user_id) REFERENCES users(user_id)
        ENABLE
    );
    --

    CREATE INDEX idx_quiz_answer_user ON quiz_answers (user_id, evaluation_name);
    --

    CREATE SEQUENCE quiz_answer_id_seq START WITH 1 INCREMENT BY 1 NOCACHE;
    --

    CREATE OR REPLACE TRIGGER trg_quiz_answer_id
        BEFORE INSERT ON quiz_answers
        FOR EACH ROW
        WHEN (NEW.quiz_answer_id IS NULL)
    BEGIN
        :NEW.quiz_answer_id := quiz_answer_id_seq.NEXTVAL;
    END;
    /
    --
