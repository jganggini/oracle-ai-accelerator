import streamlit as st
import pandas as pd
import json
from datetime import datetime
from services.database.connection import Connection

class QuizService:
    """
    Service class for managing quiz operations, including questions and user answers.
    """

    def __init__(self):
        """
        Initializes the QuizService with a shared database connection.
        """
        self.conn_instance = Connection()

    @property
    def conn(self):
        """Always returns a live connection (auto-reconnect if needed)."""
        return self.conn_instance.get_connection()
    
    def check_if_reload(self, file_id):
        """
        Verifica si un file_id corresponde a una recarga (FILE_VERSION > 1).

        Args:
            file_id (int): The ID of the file.

        Returns:
            bool: True if it's a reload (version > 1), False otherwise.
        """
        try:
            query = """
                SELECT FILE_VERSION 
                FROM FILES 
                WHERE FILE_ID = :file_id
            """
            df = pd.read_sql(query, con=self.conn, params={"file_id": file_id})
            
            if not df.empty:
                return df['FILE_VERSION'].iloc[0] > 1
            return False
            
        except Exception as e:
            print(f"Error checking reload status: {e}")
            return False

    def delete_quiz_by_file(self, file_id):
        """
        Deletes all quiz questions and answers for a specific file.
        This is used when reloading a quiz file.

        Args:
            file_id (int): The ID of the file.

        Returns:
            tuple: (success, message) indicating the result.
        """
        try:
            with self.conn.cursor() as cur:
                # First, get all quiz_ids for this file
                cur.execute("""
                    SELECT quiz_id FROM quiz WHERE file_id = :file_id
                """, {"file_id": file_id})
                quiz_ids = [row[0] for row in cur.fetchall()]

                if quiz_ids:
                    # Delete answers first (FK constraint)
                    quiz_ids_str = ','.join(map(str, quiz_ids))
                    cur.execute(f"""
                        DELETE FROM quiz_answers 
                        WHERE quiz_id IN ({quiz_ids_str})
                    """)
                    deleted_answers = cur.rowcount

                    # Then delete quiz questions
                    cur.execute("""
                        DELETE FROM quiz WHERE file_id = :file_id
                    """, {"file_id": file_id})
                    deleted_questions = cur.rowcount

                    self.conn.commit()
                    return (True, f"Deleted {deleted_answers} answer(s) and {deleted_questions} question(s)")
                else:
                    return (True, "No existing questions found to delete")

        except Exception as e:
            self.conn.rollback()
            return (False, f"Error deleting quiz data: {str(e)}")

    def insert_quiz_questions(self, file_id, questions_data, reload=False):
        """
        Inserts quiz questions from JSON data into the database.
        If reload=True, deletes existing questions first.

        Args:
            file_id (int): The ID of the uploaded file.
            questions_data (dict): The parsed JSON data containing questions.
            reload (bool): If True, deletes existing questions before inserting.

        Returns:
            str: A message indicating the result of the operation.
        """
        try:
            # If reload, delete existing data first
            if reload:
                success, msg = self.delete_quiz_by_file(file_id)
                if not success:
                    return msg

            questions = questions_data.get('questions', [])
            modules_info = {m['module']: m['percentage'] for m in questions_data.get('modules', [])}
            inserted_count = 0

            with self.conn.cursor() as cur:
                for question in questions:
                    # Obtener porcentaje del módulo
                    module_percentage = modules_info.get(question['module'], 0)
                    
                    # Insert question
                    cur.execute("""
                        INSERT INTO quiz (
                            file_id,
                            question_id,
                            module_id,
                            module_name,
                            module_percentage,
                            question_en,
                            question_es,
                            question_pt,
                            options_en,
                            options_es,
                            options_pt,
                            explanation_en,
                            explanation_es,
                            explanation_pt
                        ) VALUES (
                            :file_id,
                            :question_id,
                            :module_id,
                            :module_name,
                            :module_percentage,
                            :question_en,
                            :question_es,
                            :question_pt,
                            :options_en,
                            :options_es,
                            :options_pt,
                            :explanation_en,
                            :explanation_es,
                            :explanation_pt
                        )
                    """, {
                        "file_id": file_id,
                        "question_id": question['id'],
                        "module_id": question['module'],
                        "module_name": question['module_name'],
                        "module_percentage": module_percentage,
                        "question_en": question['question_en'],
                        "question_es": question['question_es'],
                        "question_pt": question['question_pt'],
                        "options_en": json.dumps(question['options_en']),
                        "options_es": json.dumps(question['options_es']),
                        "options_pt": json.dumps(question['options_pt']),
                        "explanation_en": question['explanation_en'],
                        "explanation_es": question['explanation_es'],
                        "explanation_pt": question['explanation_pt']
                    })
                    inserted_count += 1

            self.conn.commit()
            
            if reload:
                return f"{inserted_count} questions reloaded successfully."
            else:
                return f"{inserted_count} questions inserted successfully."
        
        except Exception as e:
            self.conn.rollback()
            return f"Error inserting questions: {str(e)}"

    @st.cache_data(show_spinner=False)
    def get_quiz_questions(_self, file_id):
        """
        Retrieves quiz questions for a specific file with all language columns.

        Args:
            file_id (int): The ID of the file.

        Returns:
            pd.DataFrame: A DataFrame containing quiz questions in all languages.
        """
        
        query = f"""
            SELECT
                quiz_id,
                question_id,
                module_id,
                module_name,
                module_percentage,
                question_en,
                question_es,
                question_pt,
                options_en,
                options_es,
                options_pt,
                explanation_en,
                explanation_es,
                explanation_pt,
                quiz_state,
                quiz_date
            FROM quiz
            WHERE file_id = {file_id}
              AND quiz_state <> 0
        """
        return pd.read_sql(query, con=_self.conn)
    
    @st.cache_data(show_spinner=False)
    def get_quiz_modules(_self, file_id):
        """
        Retrieves module distribution for a specific quiz file.

        Args:
            file_id (int): The ID of the file.

        Returns:
            pd.DataFrame: A DataFrame containing module info with percentages.
        """
        query = f"""
            SELECT DISTINCT
                module_id,
                module_name,
                module_percentage,
                COUNT(*) OVER (PARTITION BY module_id) AS question_count
            FROM quiz
            WHERE file_id = {file_id}
              AND quiz_state <> 0
            ORDER BY module_id
        """
        return pd.read_sql(query, con=_self.conn)

    def insert_quiz_answer(self, quiz_id, user_id, evaluation_name, selected_option, is_correct, answer_time_seconds=0):
        """
        Inserts a user's answer to a quiz question.

        Args:
            quiz_id (int): The ID of the quiz question.
            user_id (int): The ID of the user.
            evaluation_name (str): Name/identifier for this evaluation session.
            selected_option (int): The index of the selected option.
            is_correct (int): 1 if correct, 0 if incorrect.
            answer_time_seconds (int): Time taken to answer in seconds.

        Returns:
            str: A message indicating the result of the operation.
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO quiz_answers (
                        quiz_id,
                        user_id,
                        evaluation_name,
                        selected_option,
                        is_correct,
                        answer_time_seconds
                    ) VALUES (
                        :quiz_id,
                        :user_id,
                        :evaluation_name,
                        :selected_option,
                        :is_correct,
                        :answer_time_seconds
                    )
                """, {
                    "quiz_id": quiz_id,
                    "user_id": user_id,
                    "evaluation_name": evaluation_name,
                    "selected_option": selected_option,
                    "is_correct": is_correct,
                    "answer_time_seconds": answer_time_seconds
                })
            self.conn.commit()
            return "Answer recorded successfully."
        
        except Exception as e:
            self.conn.rollback()
            return f"Error recording answer: {str(e)}"

    @st.cache_data
    def get_user_evaluations(_self, user_id):
        """
        Retrieves all evaluations for a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            pd.DataFrame: A DataFrame containing evaluation summaries.
        """
        query = f"""
            SELECT 
                evaluation_name,
                COUNT(*) AS total_answered,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS correct_answers,
                ROUND(
                    (SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2
                ) AS score_percentage,
                MIN(quiz_answer_date) AS started_at,
                MAX(quiz_answer_date) AS completed_at
            FROM quiz_answers
            WHERE user_id = {user_id}
              AND quiz_answer_state = 1
            GROUP BY evaluation_name
            ORDER BY started_at DESC
        """
        return pd.read_sql(query, con=_self.conn)

    @st.cache_data
    def get_evaluation_results(_self, user_id, evaluation_name):
        """
        Retrieves detailed results for a specific evaluation.

        Args:
            user_id (int): The ID of the user.
            evaluation_name (str): The name of the evaluation.

        Returns:
            pd.DataFrame: A DataFrame containing detailed results.
        """
        query = """
            SELECT 
                vr.question_id,
                vr.question_en,
                vr.question_es,
                vr.question_pt,
                vr.selected_option,
                vr.is_correct,
                vr.answer_time_seconds,
                vr.quiz_answer_date,
                vr.correct_answers,
                vr.total_questions,
                vr.score_percentage
            FROM vw_quiz_results vr
            WHERE vr.user_id = :user_id
              AND vr.evaluation_name = :evaluation_name
            ORDER BY vr.question_id
        """
        return pd.read_sql(query, con=_self.conn, params={
            "user_id": user_id,
            "evaluation_name": evaluation_name
        })

    @st.cache_data
    def get_quiz_stats(_self, user_id, evaluation_name):
        """
        Retrieves statistics for a specific evaluation.

        Args:
            user_id (int): The ID of the user.
            evaluation_name (str): The name of the evaluation.

        Returns:
            pd.DataFrame: A DataFrame containing evaluation statistics.
        """
        query = """
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
            WHERE qa.user_id = :user_id
              AND qa.evaluation_name = :evaluation_name
              AND qa.quiz_answer_state <> 0
            GROUP BY 
                qa.evaluation_name,
                u.user_username,
                u.user_name,
                u.user_last_name
        """
        return pd.read_sql(query, con=_self.conn, params={
            "user_id": user_id,
            "evaluation_name": evaluation_name
        })

    def delete_evaluation(self, user_id, evaluation_name):
        """
        Soft deletes an evaluation (sets state to 0).

        Args:
            user_id (int): The ID of the user.
            evaluation_name (str): The name of the evaluation to delete.

        Returns:
            str: A message indicating the result of the operation.
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE quiz_answers
                    SET quiz_answer_state = 0
                    WHERE user_id = :user_id
                      AND evaluation_name = :evaluation_name
                """, {
                    "user_id": user_id,
                    "evaluation_name": evaluation_name
                })
            self.conn.commit()
            return f"Evaluation '{evaluation_name}' has been deleted successfully."
        
        except Exception as e:
            self.conn.rollback()
            return f"Error deleting evaluation: {str(e)}"

    def check_evaluation_exists(self, user_id, evaluation_name):
        """
        Checks if an evaluation name already exists for a user.

        Args:
            user_id (int): The ID of the user.
            evaluation_name (str): The name of the evaluation.

        Returns:
            bool: True if exists, False otherwise.
        """
        query = """
            SELECT COUNT(*) AS count
            FROM quiz_answers
            WHERE user_id = :user_id
              AND evaluation_name = :evaluation_name
              AND quiz_answer_state <> 0
        """
        df = pd.read_sql(query, con=self.conn, params={
            "user_id": user_id,
            "evaluation_name": evaluation_name
        })
        return df['COUNT'].iloc[0] > 0 if not df.empty else False
    
    def get_global_module_stats(self, start_date=None, end_date=None, file_id=None):
        """
        Get global statistics by module for all quiz answers.
        
        Args:
            start_date (str): Start date filter (YYYY-MM-DD)
            end_date (str): End date filter (YYYY-MM-DD)
            file_id (int): File ID filter for specific quiz
            
        Returns:
            pd.DataFrame: DataFrame with module statistics
        """
        query = """
            SELECT 
                q.MODULE_NAME,
                COUNT(DISTINCT qa.EVALUATION_NAME) as TOTAL_EVALUATIONS,
                COUNT(*) as TOTAL_QUESTIONS,
                SUM(qa.IS_CORRECT) as CORRECT_ANSWERS,
                ROUND(SUM(qa.IS_CORRECT) * 100.0 / COUNT(*), 2) as SCORE_PERCENTAGE
            FROM QUIZ_ANSWERS qa
            JOIN QUIZ q ON qa.QUIZ_ID = q.QUIZ_ID
            WHERE qa.QUIZ_ANSWER_STATE <> 0
        """
        
        params = {}
        if file_id:
            query += " AND q.FILE_ID = :file_id"
            params["file_id"] = file_id
        if start_date:
            query += " AND qa.QUIZ_ANSWER_DATE >= TO_DATE(:start_date, 'YYYY-MM-DD')"
            params["start_date"] = start_date
        if end_date:
            query += " AND qa.QUIZ_ANSWER_DATE < TO_DATE(:end_date, 'YYYY-MM-DD') + 1"
            params["end_date"] = end_date
        
        query += """
            GROUP BY q.MODULE_NAME
            ORDER BY SCORE_PERCENTAGE DESC
        """
        
        return pd.read_sql(query, con=self.conn, params=params if params else None)
    
    def get_top_evaluations_ranking(self, limit=5, start_date=None, end_date=None, file_id=None):
        """
        Get top evaluations ranking by score (individual evaluations, not grouped by user).
        
        Args:
            limit (int): Number of top evaluations to return
            start_date (str): Start date filter (YYYY-MM-DD)
            end_date (str): End date filter (YYYY-MM-DD)
            file_id (int): File ID filter for specific quiz
            
        Returns:
            pd.DataFrame: DataFrame with top evaluations
        """
        query = """
            SELECT 
                qa.EVALUATION_NAME,
                u.USER_USERNAME,
                u.USER_NAME || ', ' || u.USER_LAST_NAME as FULL_NAME,
                COUNT(*) as TOTAL_QUESTIONS,
                SUM(qa.IS_CORRECT) as CORRECT_ANSWERS,
                ROUND(SUM(qa.IS_CORRECT) * 100.0 / COUNT(*), 2) as SCORE,
                MIN(qa.QUIZ_ANSWER_DATE) as EVALUATION_DATE
            FROM QUIZ_ANSWERS qa
            JOIN USERS u ON qa.USER_ID = u.USER_ID
            JOIN QUIZ q ON qa.QUIZ_ID = q.QUIZ_ID
            WHERE qa.QUIZ_ANSWER_STATE <> 0
        """
        
        params = {"limit": limit}
        if file_id:
            query += " AND q.FILE_ID = :file_id"
            params["file_id"] = file_id
        if start_date:
            query += " AND qa.QUIZ_ANSWER_DATE >= TO_DATE(:start_date, 'YYYY-MM-DD')"
            params["start_date"] = start_date
        if end_date:
            query += " AND qa.QUIZ_ANSWER_DATE < TO_DATE(:end_date, 'YYYY-MM-DD') + 1"
            params["end_date"] = end_date
        
        query += """
            GROUP BY qa.EVALUATION_NAME, u.USER_USERNAME, u.USER_NAME, u.USER_LAST_NAME
            ORDER BY SCORE DESC, TOTAL_QUESTIONS DESC
            FETCH FIRST :limit ROWS ONLY
        """
        
        return pd.read_sql(query, con=self.conn, params=params)
    
    def get_quiz_summary_stats(self, start_date=None, end_date=None, file_id=None):
        """
        Get summary statistics for all quizzes.
        
        Args:
            start_date (str): Start date filter (YYYY-MM-DD)
            end_date (str): End date filter (YYYY-MM-DD)
            file_id (int): File ID filter for specific quiz
            
        Returns:
            dict: Dictionary with summary statistics
        """
        query = """
            WITH evaluation_scores AS (
                SELECT 
                    qa.EVALUATION_NAME,
                    COUNT(*) as QUESTIONS_IN_EVAL,
                    SUM(qa.IS_CORRECT) as CORRECT_IN_EVAL,
                    ROUND(SUM(qa.IS_CORRECT) * 100.0 / COUNT(*), 2) as EVAL_SCORE
                FROM QUIZ_ANSWERS qa
                JOIN QUIZ q ON qa.QUIZ_ID = q.QUIZ_ID
                WHERE qa.QUIZ_ANSWER_STATE <> 0
        """
        
        params = {}
        if file_id:
            query += " AND q.FILE_ID = :file_id"
            params["file_id"] = file_id
        if start_date:
            query += " AND qa.QUIZ_ANSWER_DATE >= TO_DATE(:start_date, 'YYYY-MM-DD')"
            params["start_date"] = start_date
        if end_date:
            query += " AND qa.QUIZ_ANSWER_DATE < TO_DATE(:end_date, 'YYYY-MM-DD') + 1"
            params["end_date"] = end_date
        
        query += """
                GROUP BY qa.EVALUATION_NAME
            )
            SELECT 
                COUNT(DISTINCT qa.USER_ID) as TOTAL_USERS,
                COUNT(DISTINCT qa.EVALUATION_NAME) as TOTAL_EVALUATIONS,
                COUNT(*) as TOTAL_QUESTIONS_ANSWERED,
                SUM(qa.IS_CORRECT) as TOTAL_CORRECT,
                ROUND(AVG(es.EVAL_SCORE), 2) as GLOBAL_AVG_SCORE
            FROM QUIZ_ANSWERS qa
            JOIN QUIZ q ON qa.QUIZ_ID = q.QUIZ_ID
            JOIN evaluation_scores es ON qa.EVALUATION_NAME = es.EVALUATION_NAME
            WHERE qa.QUIZ_ANSWER_STATE <> 0
        """
        
        if file_id:
            query += " AND q.FILE_ID = :file_id"
        if start_date:
            query += " AND qa.QUIZ_ANSWER_DATE >= TO_DATE(:start_date, 'YYYY-MM-DD')"
        if end_date:
            query += " AND qa.QUIZ_ANSWER_DATE < TO_DATE(:end_date, 'YYYY-MM-DD') + 1"
        
        df = pd.read_sql(query, con=self.conn, params=params if params else None)
        if not df.empty:
            return df.iloc[0].to_dict()
        return {}
