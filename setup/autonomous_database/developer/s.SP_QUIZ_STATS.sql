    CREATE OR REPLACE PROCEDURE sp_quiz_stats(
        p_user_id IN NUMBER,
        p_evaluation_name IN VARCHAR2
    ) AS
    BEGIN
        -- Procedimiento para obtener estadísticas de un quiz específico
        SELECT 
            qa.evaluation_name,
            u.user_username,
            u.user_name || ' ' || u.user_last_name AS user_full_name,
            COUNT(*) AS total_questions,
            SUM(CASE WHEN qa.is_correct = 1 THEN 1 ELSE 0 END) AS correct_answers,
            SUM(CASE WHEN qa.is_correct = 0 THEN 1 ELSE 0 END) AS incorrect_answers,
            ROUND(
                (SUM(CASE WHEN qa.is_correct = 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2
            ) AS score_percentage,
            SUM(qa.answer_time_seconds) AS total_time_seconds,
            ROUND(AVG(qa.answer_time_seconds), 2) AS avg_time_per_question,
            MIN(qa.quiz_answer_date) AS started_at,
            MAX(qa.quiz_answer_date) AS completed_at
        FROM quiz_answers qa
        JOIN users u ON qa.user_id = u.user_id
        WHERE qa.user_id = p_user_id
          AND qa.evaluation_name = p_evaluation_name
          AND qa.quiz_answer_state <> 0
        GROUP BY 
            qa.evaluation_name,
            u.user_username,
            u.user_name,
            u.user_last_name;
    END sp_quiz_stats;
    /
    --

