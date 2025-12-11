import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date

import components as component
import services.database as database

# Create service instances
db_quiz_service = database.QuizService()
db_file_service = database.FileService()

# Load login and footer components
st.session_state["page"] = "app_quiz_report.py"
login = component.get_login()
component.get_footer()

if login:
    st.set_page_config(layout="centered")
    
    # Check if user is Administrator
    modules = st.session_state.get("modules", "")
    if "Administrator" not in modules:
        st.error("Access denied. This page is only available for Administrators.", icon=":material/block:")
        st.stop()
    
    # Header
    st.header(":material/analytics: Quiz Reports")
    st.caption("Global statistics and performance analysis for all quizzes.")
    
    # Get quiz files for filter
    user_id = st.session_state.get("user_id")
    df_files = db_file_service.get_all_files(user_id)
    df_quiz_files = df_files[df_files["MODULE_ID"] == 8]
    
    # Filters Section
    with st.container(border=True):
        st.badge("Filters", color="blue")
        
        # First row: Quiz selector
        if not df_quiz_files.empty:
            quiz_options = ["All Quizzes"] + df_quiz_files["FILE_ID"].tolist()
            quiz_labels = {
                "All Quizzes": "All Quizzes"
            }
            for _, row in df_quiz_files.iterrows():
                quiz_labels[row["FILE_ID"]] = row["FILE_DESCRIPTION"]
            
            selected_quiz = st.selectbox(
                "Quiz",
                options=quiz_options,
                format_func=lambda x: quiz_labels.get(x, str(x)),
                help="Filter by specific quiz or view all"
            )
            
            # Convert to file_id or None for all
            file_id_filter = None if selected_quiz == "All Quizzes" else selected_quiz
        else:
            file_id_filter = None
        
        # Second row: Date filters
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=None,
                help="Filter evaluations from this date onwards (leave empty for all)"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=None,
                help="Filter evaluations up to this date (leave empty for all)"
            )
        
        # Third row: Search button (below)
        if st.button(":material/search: Search", type="secondary", width="stretch"):
            st.cache_data.clear()
            st.rerun()
        
        # Convert dates to strings for SQL
        start_date_str = start_date.strftime('%Y-%m-%d') if start_date else None
        end_date_str = end_date.strftime('%Y-%m-%d') if end_date else None
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            st.error("Start Date cannot be after End Date. Please adjust the date range.", icon=":material/error:")
            st.stop()
        
    
    # Get summary statistics
    try:
        summary_stats = db_quiz_service.get_quiz_summary_stats(
            start_date=start_date_str,
            end_date=end_date_str,
            file_id=file_id_filter
        )
        
        if summary_stats and summary_stats.get('TOTAL_EVALUATIONS'):
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    ":material/assignment: Total Evaluations",
                    f"{(summary_stats.get('TOTAL_EVALUATIONS') or 0):,}",
                    border=True
                )
            
            with col2:
                st.metric(
                    ":material/quiz: Questions Answered",
                    f"{(summary_stats.get('TOTAL_QUESTIONS_ANSWERED') or 0):,}",
                    border=True
                )
            
            with col3:
                st.metric(
                    ":material/check_circle: Correct Answers",
                    f"{(summary_stats.get('TOTAL_CORRECT') or 0):,}",
                    border=True
                )
            
            with col4:
                st.metric(
                    ":material/score: Global Avg Score",
                    f"{(summary_stats.get('GLOBAL_AVG_SCORE') or 0):.1f}%",
                    border=True
                )
            
            
            # Module Performance Section
            df_module_stats = db_quiz_service.get_global_module_stats(
                start_date=start_date_str,
                end_date=end_date_str,
                file_id=file_id_filter
            )
            
            if not df_module_stats.empty:
                # Replace None values with 0 for proper formatting
                df_module_stats = df_module_stats.fillna(0)
                
                # Best performing module
                best_module = df_module_stats.iloc[0]
                st.success(
                    f"🏆 **Best Performing Module:** {best_module['MODULE_NAME']} "
                    f"({best_module['SCORE_PERCENTAGE']:.1f}% average score)",
                    icon=":material/emoji_events:"
                )
                
                # Create chart
                chart = (
                    alt.Chart(df_module_stats)
                    .mark_bar()
                    .encode(
                        y=alt.Y("MODULE_NAME:N", sort="-x", title="Module"),
                        x=alt.X("SCORE_PERCENTAGE:Q", title="Average Score (%)", scale=alt.Scale(domain=[0, 100])),
                        color=alt.Color(
                            "SCORE_PERCENTAGE:Q",
                            scale=alt.Scale(scheme="greenblue"),
                            legend=None
                        ),
                        tooltip=[
                            alt.Tooltip("MODULE_NAME:N", title="Module"),
                            alt.Tooltip("SCORE_PERCENTAGE:Q", title="Avg Score (%)", format=".2f"),
                            alt.Tooltip("CORRECT_ANSWERS:Q", title="Correct Answers"),
                            alt.Tooltip("TOTAL_QUESTIONS:Q", title="Total Questions")
                        ]
                    )
                    .properties(height=400)
                )
                
                with st.container(border=True):
                    st.altair_chart(chart, use_container_width=True)
                
                # Detail table
                st.dataframe(
                    df_module_stats,
                    hide_index=True,
                    width="stretch",
                    column_config={
                        "MODULE_NAME": st.column_config.TextColumn("Module", width="large"),
                        "TOTAL_EVALUATIONS": st.column_config.NumberColumn("Evaluations", format="%d"),
                        "TOTAL_QUESTIONS": st.column_config.NumberColumn("Questions", format="%d"),
                        "CORRECT_ANSWERS": st.column_config.NumberColumn("Correct", format="%d"),
                        "SCORE_PERCENTAGE": st.column_config.ProgressColumn(
                            "Avg Score",
                            format="%.2f%%",
                            min_value=0,
                            max_value=100
                        )
                    }
                )
            else:
                st.info("No module data available yet.", icon=":material/info:")
            
            
            # Top Evaluations Ranking
            st.subheader(":material/leaderboard: Top 5 Evaluations Ranking")
            st.caption("Individual evaluations ranked by score")
            
            df_top_evals = db_quiz_service.get_top_evaluations_ranking(
                limit=3,
                start_date=start_date_str,
                end_date=end_date_str,
                file_id=file_id_filter
            )
            
            if not df_top_evals.empty:
                # Display ranking with medals
                for idx, evaluation in df_top_evals.iterrows():
                    rank = idx + 1
                    
                    # Medal icons
                    if rank == 1:
                        medal = "🥇"
                    elif rank == 2:
                        medal = "🥈"
                    elif rank == 3:
                        medal = "🥉"
                    else:
                        medal = f"#{rank}"
                    
                    # Parse evaluation name (format: "name - date" or "name-date")
                    eval_name_full = evaluation['EVALUATION_NAME']
                    if ' - ' in eval_name_full:
                        eval_name, eval_date = eval_name_full.split(' - ', 1)
                    elif '-' in eval_name_full:
                        parts = eval_name_full.split('-', 1)
                        eval_name = parts[0]
                        eval_date = parts[1] if len(parts) > 1 else ""
                    else:
                        eval_name = eval_name_full
                        eval_date = ""
                    
                    # Extract only numeric date (remove spaces, colons, etc.)
                    eval_date_numeric = ''.join(filter(str.isdigit, eval_date))
                    
                    # Convert numeric date to readable format
                    try:
                        if len(eval_date_numeric) >= 14:
                            # Format: YYYYMMDDHHmmss
                            dt = datetime.strptime(eval_date_numeric[:14], '%Y%m%d%H%M%S')
                            eval_date_formatted = dt.strftime('%d/%m/%Y %H:%M:%S')
                        elif len(eval_date_numeric) >= 8:
                            # Format: YYYYMMDD
                            dt = datetime.strptime(eval_date_numeric[:8], '%Y%m%d')
                            eval_date_formatted = dt.strftime('%d/%m/%Y')
                        else:
                            eval_date_formatted = eval_date_numeric
                    except:
                        eval_date_formatted = eval_date_numeric
                    
                    with st.container(border=True):
                        col1, col2, col3, col4 = st.columns([0.5, 3, 1, 1])
                        
                        with col1:
                            st.markdown(f"### {medal}")
                        
                        with col2:
                            st.markdown(f"**@{eval_name}**")
                            st.caption(f"📅 {eval_date_formatted}")
                        
                        with col3:
                            st.metric("Score", f"{evaluation['SCORE']:.1f}%")
                        
                        with col4:
                            st.metric("Questions", f"{evaluation['TOTAL_QUESTIONS']}")
                
                
            else:
                st.info("No evaluation data available yet.", icon=":material/info:")
        
        else:
            st.warning("No quiz data available. Complete some quizzes to see statistics.", icon=":material/warning:")
    
    except Exception as e:
        st.error(f"Error loading quiz reports: {e}", icon=":material/error:")

