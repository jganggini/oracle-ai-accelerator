    CREATE OR REPLACE VIEW vw_quiz_results AS
    SELECT 
        qa.quiz_answer_id,
        qa.user_id,
        u.user_username,
        u.user_name || ' ' || u.user_last_name AS user_full_name,
        qa.evaluation_name,
        q.quiz_id,
        q.file_id,
        f.file_name,
        q.question_id,
        q.module_id,
        q.module_name,
        q.question_en,
        q.question_es,
        q.question_pt,
        qa.selected_option,
        qa.is_correct,
        qa.answer_time_seconds,
        qa.quiz_answer_date,
        -- Calcular estadísticas por evaluación
        (
            SELECT COUNT(*)
            FROM quiz_answers qa2
            WHERE qa2.user_id = qa.user_id
              AND qa2.evaluation_name = qa.evaluation_name
              AND qa2.is_correct = 1
        ) AS correct_answers,
        (
            SELECT COUNT(*)
            FROM quiz_answers qa2
            WHERE qa2.user_id = qa.user_id
              AND qa2.evaluation_name = qa.evaluation_name
        ) AS total_questions,
        (
            SELECT ROUND(
                (COUNT(CASE WHEN qa2.is_correct = 1 THEN 1 END) * 100.0) / COUNT(*), 2
            )
            FROM quiz_answers qa2
            WHERE qa2.user_id = qa.user_id
              AND qa2.evaluation_name = qa.evaluation_name
        ) AS score_percentage
    FROM quiz_answers qa
    JOIN quiz q ON qa.quiz_id = q.quiz_id
    JOIN users u ON qa.user_id = u.user_id
    JOIN files f ON q.file_id = f.file_id
    WHERE qa.quiz_answer_state <> 0
      AND q.quiz_state <> 0;
    --

