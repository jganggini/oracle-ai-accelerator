import time
import json
import random
import pandas as pd
import altair as alt
from datetime import datetime
import streamlit as st

import components as component
import services.database as database

# Create service instances
db_quiz_service = database.QuizService()
db_file_service = database.FileService()

# Load login and footer components
st.session_state["page"] = "app_quiz.py"
login = component.get_login()
component.get_footer()

if login:
    st.set_page_config(layout="centered")
    
    username = st.session_state["username"]
    user_id = st.session_state["user_id"]
    
    # Header
    st.header(":material/quiz: Quiz")
    st.caption("Test your knowledge with our interactive quizzes.")
    
    # Initialize session states
    if "quiz_started" not in st.session_state:
        st.session_state["quiz_started"] = False
        st.session_state["quiz_questions"] = []
        st.session_state["quiz_current_index"] = 0
        st.session_state["quiz_answers"] = {}
        st.session_state["quiz_start_time"] = None
        st.session_state["quiz_evaluation_name"] = ""
        st.session_state["quiz_file_id"] = None
        st.session_state["quiz_finished"] = False

    # Get available quiz files for user
    df_files = db_file_service.get_all_files(user_id)
    df_quiz_files = df_files[df_files["MODULE_ID"] == 8]

    if df_quiz_files.empty:
        st.info("No quizzes available. Please contact the administrator.", icon=":material/info:")
    else:
        # Quiz not started
        if not st.session_state["quiz_started"]:
            with st.container(border=True):
                st.badge("Quiz Configuration", color="blue")
                
                # Quiz selector comes from sidebar (Options)
                selected_file_id = st.session_state.get("quiz_selected_file_id")
                if not selected_file_id:
                    st.info("Select a quiz file from Options to continue.", icon=":material/info:")
                    st.stop()
                
                # Get available questions and modules
                df_all_questions = db_quiz_service.get_quiz_questions(selected_file_id)
                df_modules = db_quiz_service.get_quiz_modules(selected_file_id)
                total_available = len(df_all_questions)
                
                # Show module distribution
                with st.expander("Module Distribution"):
                    for _, module in df_modules.iterrows():
                        st.caption(f"**{module['MODULE_NAME']}**: {module['MODULE_PERCENTAGE']}% ({module['QUESTION_COUNT']} questions)")
                
                st.caption(f"Total available questions: **{total_available}**")
                
                # Number of questions selector
                num_questions = st.number_input(
                    "Number of questions for evaluation",
                    min_value=1,
                    max_value=total_available,
                    value=min(10, total_available),
                    step=1,
                    help="Questions will be distributed proportionally according to each module's percentage"
                )
                
                # Evaluation name
                evaluation_name_input = st.text_input(
                    "Evaluation Name",
                    value="",
                    placeholder="Enter evaluation name...",
                    help="Enter a name for this evaluation (date will be added automatically)"
                )
                
                # Language selector (checkboxes) with order tracking
                st.markdown("**Languages**")
                
                # Initialize language order tracking in session state
                if "quiz_lang_order" not in st.session_state:
                    st.session_state["quiz_lang_order"] = []
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    lang_es = st.checkbox("Español", value=False, key="lang_es")
                with col2:
                    lang_en = st.checkbox("English", value=False, key="lang_en")
                with col3:
                    lang_pt = st.checkbox("Português", value=False, key="lang_pt")
                
                # Update language order based on selection
                current_selections = {"es": lang_es, "en": lang_en, "pt": lang_pt}
                
                # Remove unselected languages from order
                st.session_state["quiz_lang_order"] = [
                    lang for lang in st.session_state["quiz_lang_order"] 
                    if current_selections.get(lang, False)
                ]
                
                # Add newly selected languages to order
                for lang_code, is_selected in current_selections.items():
                    if is_selected and lang_code not in st.session_state["quiz_lang_order"]:
                        st.session_state["quiz_lang_order"].append(lang_code)
                
                selected_langs = st.session_state["quiz_lang_order"]
                
                # Show selection order if languages are selected
                if len(selected_langs) > 0:
                    lang_names = {"es": "Español", "en": "English", "pt": "Português"}
                    order_display = " → ".join([lang_names[lang] for lang in selected_langs])
                    if len(selected_langs) == 1:
                        st.caption(f"Selected: {order_display}")
                    else:
                        st.caption(f"Order: {order_display} (Primary → Secondary)")
                
                st.divider()
                
                # Start Quiz button (always visible)
                if st.button("Start Quiz", type="primary", icon=":material/play_arrow:", width="stretch"):
                    # Validate inputs when button is pressed
                    if len(selected_langs) == 0:
                        st.info("You must select at least one language.", icon=":material/warning:")
                    elif len(selected_langs) > 2:
                        st.info("You can select a maximum of 2 languages.", icon=":material/warning:")
                    elif not evaluation_name_input or evaluation_name_input.strip() == "":
                        st.info("You must enter an **Evaluation Name** before starting.", icon=":material/warning:")
                    else:
                        try:
                            evaluation_name = f"{evaluation_name_input.strip()}-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"
                            
                            if db_quiz_service.check_evaluation_exists(user_id, evaluation_name):
                                st.error("An evaluation with this name already exists. Please use a different name.", icon=":material/error:")
                            else:
                                component.get_processing(True)
                                
                                # Get questions and modules
                                df_modules = db_quiz_service.get_quiz_modules(selected_file_id)
                                
                                # Select questions by module distribution
                                selected_questions = []
                                for _, module in df_modules.iterrows():
                                    module_id = module["MODULE_ID"]
                                    percentage = module["MODULE_PERCENTAGE"]
                                    num_for_module = max(1, int(num_questions * percentage / 100))
                                    module_questions = df_all_questions[df_all_questions["MODULE_ID"] == module_id]
                                    if len(module_questions) >= num_for_module:
                                        selected = module_questions.sample(n=num_for_module).to_dict("records")
                                    else:
                                        selected = module_questions.to_dict("records")
                                    selected_questions.extend(selected)
                                
                                # Adjust to exact number of questions
                                if len(selected_questions) > num_questions:
                                    selected_questions = random.sample(selected_questions, num_questions)
                                elif len(selected_questions) < num_questions:
                                    remaining = num_questions - len(selected_questions)
                                    all_ids = {q["QUIZ_ID"] for q in selected_questions}
                                    available = df_all_questions[~df_all_questions["QUIZ_ID"].isin(all_ids)]
                                    if len(available) >= remaining:
                                        extra = available.sample(n=remaining).to_dict("records")
                                        selected_questions.extend(extra)
                                
                                # Shuffle questions
                                random.shuffle(selected_questions)
                                
                                # Shuffle options synchronized across all languages
                                for question in selected_questions:
                                    # Parse all language options first
                                    all_lang_options = {}
                                    for lang in selected_langs:
                                        lang_upper = lang.upper()
                                        options_data = question[f"OPTIONS_{lang_upper}"]
                                        if isinstance(options_data, str):
                                            options = json.loads(options_data)
                                        else:
                                            options = options_data
                                        all_lang_options[lang_upper] = options
                                    
                                    # Generate a single shuffle order based on first language
                                    first_lang = selected_langs[0].upper()
                                    num_options = len(all_lang_options[first_lang])
                                    shuffle_indices = list(range(num_options))
                                    random.shuffle(shuffle_indices)
                                    
                                    # Apply the same shuffle order to all languages
                                    for lang_upper, options in all_lang_options.items():
                                        shuffled_options = [options[i] for i in shuffle_indices]
                                        question[f"OPTIONS_{lang_upper}"] = shuffled_options
                                
                                # Start quiz
                                st.session_state["quiz_started"] = True
                                st.session_state["quiz_questions"] = selected_questions
                                st.session_state["quiz_current_index"] = 0
                                st.session_state["quiz_answers"] = {}
                                st.session_state["quiz_start_time"] = time.time()
                                st.session_state["quiz_evaluation_name"] = evaluation_name
                                st.session_state["quiz_file_id"] = selected_file_id
                                st.session_state["quiz_languages"] = selected_langs
                                st.session_state["quiz_finished"] = False
                                
                                component.get_processing(False)
                                st.rerun()
                                
                        except Exception as e:
                            component.get_processing(False)
                            st.error(f"Error starting quiz: {e}", icon=":material/error:")
        # Quiz in progress
        elif st.session_state["quiz_started"] and not st.session_state["quiz_finished"]:
            questions = st.session_state["quiz_questions"]
            current_idx = st.session_state["quiz_current_index"]
            selected_langs = st.session_state["quiz_languages"]
            
            if current_idx < len(questions):
                question = questions[current_idx]
                
                # Show progress and timer
                st.progress((current_idx + 1) / len(questions), text=f"Question {current_idx + 1} of {len(questions)}")
                
                with st.container(border=True):
                    # Question module
                    st.caption(f"📚 {question['MODULE_NAME']}")
                    
                    # Primary language (convert to uppercase for columns)
                    primary_lang = selected_langs[0].upper()
                    
                    # If second language, show both with line break
                    if len(selected_langs) == 2:
                        secondary_lang = selected_langs[1].upper()
                        st.markdown(f"##### {question[f'QUESTION_{primary_lang}']}\n:gray[{question[f'QUESTION_{secondary_lang}']}]")
                    else:
                        st.markdown(f"##### {question[f'QUESTION_{primary_lang}']}")
                    
                    # Options (can come as string or list)
                    options_data = question[f'OPTIONS_{primary_lang}']
                    options_primary = json.loads(options_data) if isinstance(options_data, str) else options_data
                    
                    # Build option labels
                    option_labels = []
                    if len(selected_langs) == 2:
                        secondary_lang = selected_langs[1].upper()
                        sec_options_data = question[f'OPTIONS_{secondary_lang}']
                        options_secondary = json.loads(sec_options_data) if isinstance(sec_options_data, str) else sec_options_data
                        
                        for idx, opt in enumerate(options_primary):
                            label = f"{opt['text']}\n\n:gray[{options_secondary[idx]['text']}]"
                            option_labels.append(label)
                    else:
                        option_labels = [opt['text'] for opt in options_primary]
                    
                    # Radio button for selection
                    selected_option = st.radio(
                        "Select your answer:",
                        options=range(len(options_primary)),
                        format_func=lambda x: option_labels[x],
                        key=f"question_{current_idx}",
                        index=st.session_state.get(f"saved_option_{current_idx}", None)
                    )
                    
                    # Validation message placeholder
                    validation_msg = st.empty()
                    
                    st.divider()
                    
                    # Navigation buttons
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        if current_idx > 0:
                            if st.button("← Previous", width="stretch"):
                                st.session_state["quiz_current_index"] -= 1
                                st.rerun()
                    
                    with col3:
                        if current_idx < len(questions) - 1:
                            if st.button("Next →", type="primary", width="stretch"):
                                # Validate that an option was selected
                                if selected_option is None:
                                    validation_msg.warning("Please select an answer before continuing.", icon=":material/warning:")
                                else:
                                    # Save answer
                                    is_correct = options_primary[selected_option]['isCorrect']
                                    
                                    st.session_state["quiz_answers"][current_idx] = {
                                        "quiz_id": question['QUIZ_ID'],
                                        "selected_option": selected_option,
                                        "is_correct": 1 if is_correct else 0
                                    }
                                    
                                    # Save selection to allow going back
                                    st.session_state[f"saved_option_{current_idx}"] = selected_option
                                    
                                    st.session_state["quiz_current_index"] += 1
                                    st.rerun()
                        else:
                            # Last question - Finish button
                            if st.button("Finish", type="primary", icon=":material/check_circle:", width="stretch"):
                                # Validate that an option was selected
                                if selected_option is None:
                                    validation_msg.warning("Please select an answer before finishing.", icon=":material/warning:")
                                else:
                                    # Save last answer
                                    is_correct = options_primary[selected_option]['isCorrect']
                                    
                                    st.session_state["quiz_answers"][current_idx] = {
                                        "quiz_id": question['QUIZ_ID'],
                                        "selected_option": selected_option,
                                        "is_correct": 1 if is_correct else 0
                                    }
                                    
                                    # Save all answers to database
                                    try:
                                        component.get_processing(True)
                                        evaluation_name = st.session_state["quiz_evaluation_name"]
                                        
                                        for answer_data in st.session_state["quiz_answers"].values():
                                            db_quiz_service.insert_quiz_answer(
                                                quiz_id=answer_data["quiz_id"],
                                                user_id=user_id,
                                                evaluation_name=evaluation_name,
                                                selected_option=answer_data["selected_option"],
                                                is_correct=answer_data["is_correct"]
                                            )
                                        
                                        st.session_state["quiz_finished"] = True
                                        component.get_processing(False)
                                        st.rerun()
                                        
                                    except Exception as e:
                                        component.get_processing(False)
                                        st.error(f"Error saving answers: {e}")
        
        # Quiz finished - show results
        elif st.session_state["quiz_finished"]:
            answers = st.session_state["quiz_answers"]
            total_questions = len(answers)
            correct_answers = sum(1 for ans in answers.values() if ans["is_correct"] == 1)
            incorrect_answers = total_questions - correct_answers
            score_percentage = (correct_answers / total_questions) * 100
            total_time = int(time.time() - st.session_state["quiz_start_time"])
            avg_time = total_time / total_questions
            
            with st.container(border=True):                
                st.badge("Evaluation", color="blue")
                st.markdown(f"### {st.session_state['quiz_evaluation_name']}")
                
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(":material/check_circle: Correct", correct_answers, border=True)
            with col2:
                st.metric(":material/cancel: Incorrect", incorrect_answers, border=True)
            with col3:
                st.metric(":material/score: Score", f"{score_percentage:.1f}%", border=True)
            with col4:
                st.metric(":material/timer: Time", f"{total_time // 60}:{total_time % 60:02d}", border=True)
                
            # Calculate statistics by module
            questions = st.session_state["quiz_questions"]
            module_stats = {}
            
            for idx, question in enumerate(questions):
                module_name = question['MODULE_NAME']
                if module_name not in module_stats:
                    module_stats[module_name] = {
                        'total': 0,
                        'correct': 0,
                        'percentage_weight': question['MODULE_PERCENTAGE']
                    }
                
                module_stats[module_name]['total'] += 1
                if answers[idx]['is_correct'] == 1:
                    module_stats[module_name]['correct'] += 1
                
            # Create DataFrame for chart
            chart_data = []
            for module_name, stats in module_stats.items():
                score = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
                chart_data.append({
                    'Module': module_name,
                    'Score (%)': score,
                    'Correct': stats['correct'],
                    'Total': stats['total'],
                    'Weight': stats['percentage_weight']
                })
            
            df_chart = pd.DataFrame(chart_data)
            df_chart = df_chart.sort_values('Module')
                
            # Bar chart horizontal con leyenda de colores para cada módulo
            chart = (
                alt.Chart(df_chart)
                .mark_bar()
                .encode(
                    y=alt.Y("Module:N", sort="-x", title="Module"),
                    x=alt.X("Score (%):Q", title="Score (%)"),
                    color=alt.Color(
                        "Module:N",
                        legend=None
                    )
                )
                .properties(height=300)
            )
            
            with st.container(border=True):
                st.altair_chart(chart, use_container_width=True)
            
                
            # Detail table
            st.dataframe(
                df_chart,
                hide_index=True,
                width="stretch",
                column_config={
                    "Module": st.column_config.TextColumn("Module", width="large"),
                    "Score (%)": st.column_config.NumberColumn("Score (%)", format="%.1f%%"),
                    "Correct": st.column_config.NumberColumn("Correct"),
                    "Total": st.column_config.NumberColumn("Total"),
                    "Weight": st.column_config.NumberColumn("Weight (%)", format="%d%%")
                }
            )
            
            # Show answer review
            with st.expander("View Detailed Review", expanded=False):
                primary_lang = st.session_state["quiz_languages"][0]
                secondary_lang = st.session_state["quiz_languages"][1] if len(st.session_state["quiz_languages"]) == 2 else None
                
                for idx, question in enumerate(questions):
                    answer = answers[idx]
                    primary_lang_upper = primary_lang.upper()
                    
                    # Options (can come as string or list)
                    options_data = question[f'OPTIONS_{primary_lang_upper}']
                    options = json.loads(options_data) if isinstance(options_data, str) else options_data
                    selected_opt = answer["selected_option"]
                    
                    # Find correct answer
                    correct_opt_idx = next((i for i, opt in enumerate(options) if opt['isCorrect']), None)
                    
                    with st.container(border=True):
                        # Question header
                        if answer["is_correct"] == 1:
                            st.success(f"**Question {idx + 1}**", icon=":material/check_circle:")
                        else:
                            st.error(f"**Question {idx + 1}**", icon=":material/cancel:")
                        
                        # Module
                        st.caption(f"📚 {question['MODULE_NAME']}")
                        
                        # Question
                        st.markdown(f"**{question[f'QUESTION_{primary_lang_upper}']}**")
                        
                        # Selected answer
                        st.markdown(f"**Your answer:** {options[selected_opt]['text']}")
                        
                        # If incorrect, show correct answer
                        if answer["is_correct"] == 0 and correct_opt_idx is not None:
                            st.info(f"**Correct answer:** {options[correct_opt_idx]['text']}")
                        
                        # Explanation
                        if question.get(f'EXPLANATION_{primary_lang_upper}'):
                            with st.expander(":material/lightbulb: View Explanation"):
                                st.markdown(question[f'EXPLANATION_{primary_lang_upper}'])
            
            st.divider()
            
            # Button to take a new quiz
            if st.button("Take Another Quiz", type="primary", icon=":material/refresh:", use_container_width=True):
                # Reset all quiz states including language order
                st.session_state["quiz_started"] = False
                st.session_state["quiz_questions"] = []
                st.session_state["quiz_current_index"] = 0
                st.session_state["quiz_answers"] = {}
                st.session_state["quiz_start_time"] = None
                st.session_state["quiz_evaluation_name"] = ""
                st.session_state["quiz_file_id"] = None
                st.session_state["quiz_finished"] = False
                st.session_state["quiz_lang_order"] = []
                # Clear saved options
                keys_to_delete = [key for key in st.session_state.keys() if key.startswith("saved_option_")]
                for key in keys_to_delete:
                    del st.session_state[key]
                st.rerun()
