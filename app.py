import streamlit as st
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from pdf_utils import extract_text
from vector_store import split_text, create_vector_store, search_pdf
from llm_handler import get_answer, generate_quiz, generate_flashcards, generate_summary, socratic_tutor, generate_exam
from voice_utils import listen_from_microphone, transcribe_audio_file
@st.cache_resource
def get_vector_store(chunks_tuple):
    return create_vector_store(list(chunks_tuple))

st.title("📚 AI Study Copilot")

# Multi PDF upload
pdfs = st.file_uploader(
    "Upload one or more PDFs",
    type="pdf",
    accept_multiple_files=True
)

if pdfs:
    st.success(f" {len(pdfs)} PDF(s) Uploaded Successfully!")

    # Extract and combine text from all PDFs
    all_chunks = []
    pdf_chunk_map = {}  # to know which chunk belong to which PDF
    with st.expander(" Uploaded Files"):
        for pdf in pdfs:
            st.write(f"📄 {pdf.name}")
            text = extract_text(pdf)
            chunks = split_text(text)
            pdf_chunk_map[pdf.name] = chunks
            all_chunks.extend(chunks)

    st.info(f" Total Chunks from all PDFs: {len(all_chunks)}")

    # Create combined vector store
    vector_db = get_vector_store(tuple(all_chunks))
    st.success(" FAISS Vector Database Ready!")

    # Tabs available
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "💬 Chat",
    "📝 Quiz Generator",
    "🃏 Flashcards",
    "📋 Summarizer",
    "🧠 Socratic Tutor",
    "📊 Exam Simulator",
    "🎤 Voice Input"
])

    # Tab:1 Chat 
    with tab1:
        st.subheader(" Chat with your PDFs")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if message["role"] == "assistant" and "sources" in message:
                    with st.expander("📄 View Sources"):
                        for i, source in enumerate(message["sources"]):
                            st.markdown(f"**Chunk {i+1}:**")
                            st.info(source[:300] + "...")

        query = st.chat_input("Ask something about your PDF(s)...")

        if query:
            with st.chat_message("user"):
                st.write(query)
            st.session_state.chat_history.append({
                "role": "user",
                "content": query
            })

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    results = search_pdf(vector_db, query)
                    answer = get_answer(query, results)
                    st.write(answer)
                    sources = [r.page_content for r in results]
                    with st.expander("📄 View Sources"):
                        for i, source in enumerate(sources):
                            st.markdown(f"**Chunk {i+1}:**")
                            st.info(source[:300] + "...")

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })

    # Tab:2 Quiz Generator
    with tab2:
        st.subheader(" Auto Quiz Generator")
        st.write("Generate MCQ questions automatically from your PDF!")

        num_q = st.slider("How many questions?", min_value=3, max_value=10, value=5)

        if st.button(" Generate Quiz"):
            with st.spinner("Generating quiz..."):
                quiz_text = generate_quiz(all_chunks, num_questions=num_q, pdf_chunk_map=pdf_chunk_map)
                st.session_state.quiz = quiz_text

        if "quiz" in st.session_state:
            st.markdown("---")
            st.subheader("Your Quiz")
            questions = st.session_state.quiz.split("---")
            for i, q in enumerate(questions):
                if q.strip():
                    with st.expander(f"Question {i+1}", expanded=True):
                        lines = q.strip().split("\n")
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            if line.startswith("Q"):
                                st.markdown(f"**{line}**")
                            elif line.startswith("Answer:"):
                                st.success(f"✅ {line}")
                            elif line.startswith("Explanation:"):
                                st.info(f"💡 {line}")
                            else:
                                st.write(line)

            st.download_button(
                label="⬇️ Download Quiz",
                data=st.session_state.quiz,
                file_name="quiz.txt",
                mime="text/plain"
            )

    # Tab:3 Flashcard Generator
    with tab3:
        st.subheader(" Flashcard Generator")
        st.write("Generate study flashcards automatically from your PDF!")

        num_cards = st.slider("How many flashcards?", min_value=5, max_value=20, value=10)

        if st.button(" Generate Flashcards"):
            with st.spinner("Creating flashcards..."):
                flashcard_text = generate_flashcards(all_chunks, num_cards=num_cards, pdf_chunk_map=pdf_chunk_map)
                st.session_state.flashcards = flashcard_text

        if "flashcards" in st.session_state:
            cards = st.session_state.flashcards.split("---")

            if "flipped" not in st.session_state:
                st.session_state.flipped = {}

            st.markdown("---")
            st.subheader("Your Flashcards")
            st.info(" Click the button below each card to flip it!")

            cols = st.columns(2)
            card_num = 0

            for card in cards:
                if "FRONT:" not in card:
                    continue

                lines = card.strip().split("\n")
                front, back = "", ""
                for line in lines:
                    if line.startswith("FRONT:"):
                        front = line.replace("FRONT:", "").strip()
                    elif line.startswith("BACK:"):
                        back = line.replace("BACK:", "").strip()

                if front and back:
                    col = cols[card_num % 2]
                    with col:
                        is_flipped = st.session_state.flipped.get(card_num, False)

                        if not is_flipped:
                            st.markdown(f"""
                            <div style="
                                background: #1a73e8;
                                color: white;
                                padding: 20px;
                                border-radius: 12px;
                                min-height: 120px;
                                margin-bottom: 8px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                text-align: center;
                                font-size: 15px;
                                font-weight: 500;
                            ">
                                ❓ {front}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="
                                background: #0f9d58;
                                color: white;
                                padding: 20px;
                                border-radius: 12px;
                                min-height: 120px;
                                margin-bottom: 8px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                text-align: center;
                                font-size: 15px;
                            ">
                                ✅ {back}
                            </div>
                            """, unsafe_allow_html=True)

                        if st.button(
                            "🔄 Flip Card",
                            key=f"card_{card_num}",
                            use_container_width=True
                        ):
                            st.session_state.flipped[card_num] = not is_flipped
                            st.rerun()

                    card_num += 1

            st.download_button(
                label="⬇️ Download Flashcards",
                data=st.session_state.flashcards,
                file_name="flashcards.txt",
                mime="text/plain"
            )

    # Tab:4 Summarizer
    with tab4:
        st.subheader(" Smart Summarizer")
        st.write("Get a complete summary of your PDF in seconds!")

        if st.button(" Generate Summary"):
            with st.spinner("Summarizing your PDF..."):
                summary = generate_summary(all_chunks, pdf_chunk_map=pdf_chunk_map)
                st.session_state.summary = summary

        if "summary" in st.session_state:
            st.markdown("---")
            lines = st.session_state.summary.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("📌") or line.startswith("🔑") or line.startswith("📝") or line.startswith("💡") or line.startswith("⭐"):
                    st.markdown(f"### {line}")
                elif line[0].isdigit() and "." in line[:3]:
                    st.markdown(f"**{line}**")
                elif line.startswith("•"):
                    st.markdown(line)
                else:
                    st.write(line)

            st.markdown("---")
            st.download_button(
                label="⬇️ Download Summary",
                data=st.session_state.summary,
                file_name="summary.txt",
                mime="text/plain"
            )
    # Tab:5 Socratic Tutor
    with tab5:
        st.subheader(" Socratic Tutor Mode")
        st.write("I won't give you the answer — I'll help you **think** and figure it out yourself!")

        st.info("💡 This mode asks you guiding questions instead of giving direct answers — just like a real tutor!")

        # Mode explanation
        col1, col2 = st.columns(2)
        with col1:
            st.error("❌ Normal mode: Here is the answer...")
        with col2:
            st.success("✅ Socratic mode: What do you think happens when...?")

        st.markdown("---")

        # Chat history for socratic mode
        if "socratic_history" not in st.session_state:
            st.session_state.socratic_history = []

        # Show previous messages
        for message in st.session_state.socratic_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Chat input
        socratic_query = st.chat_input("Ask your question and I'll guide you to the answer...")

        if socratic_query:
            with st.chat_message("user"):
                st.write(socratic_query)
            st.session_state.socratic_history.append({
                "role": "user",
                "content": socratic_query
            })

            with st.chat_message("assistant"):
                with st.spinner("Thinking of guiding questions..."):
                    results = search_pdf(vector_db, socratic_query)
                    response = socratic_tutor(socratic_query, results)
                    st.write(response)

            st.session_state.socratic_history.append({
                "role": "assistant",
                "content": response
            })

        # Clear button
        if st.session_state.socratic_history:
            if st.button("🗑️ Clear Conversation"):
                st.session_state.socratic_history = []
                st.rerun()
    # Tab:6 Exam Simulator
    with tab6:
        st.subheader(" Exam Simulator")
        st.write("Take a real timed exam based on your PDF!")

        # Exam settings
        col1, col2 = st.columns(2)
        with col1:
            num_q = st.slider(
                "Number of questions",
                min_value=5,
                max_value=15,
                value=10
            )
        with col2:
            difficulty = st.selectbox(
                "Difficulty",
                ["Easy", "Medium", "Hard"]
            )

        # Timer setting
        time_limit = st.selectbox(
            "Time limit",
            ["5 minutes", "10 minutes", "15 minutes", "20 minutes", "No limit"]
        )

        if st.button(" Start Exam"):
            with st.spinner("Generating your exam..."):
                exam_text = generate_exam(
                    all_chunks,
                    num_questions=num_q,
                    difficulty=difficulty,
                    pdf_chunk_map=pdf_chunk_map
                )
                st.session_state.exam_text = exam_text
                st.session_state.exam_answers = {}
                st.session_state.exam_submitted = False
                st.session_state.exam_score = 0

                # Parse questions
                questions = []
                current_q = {}
                for line in exam_text.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("---"):
                        if current_q.get("question"):
                            questions.append(current_q)
                            current_q = {}
                    elif line.startswith("Q") and ":" in line[:4]:
                        current_q["question"] = line.split(":", 1)[1].strip()
                        current_q["options"] = []
                    elif line.startswith(("A)", "B)", "C)", "D)")):
                        current_q.setdefault("options", []).append(line)
                    elif line.startswith("ANSWER:"):
                        current_q["answer"] = line.replace("ANSWER:", "").strip()

                if current_q.get("question"):
                    questions.append(current_q)

                st.session_state.exam_questions = questions

                # Set timer
                if time_limit != "No limit":
                    minutes = int(time_limit.split()[0])
                    import time
                    st.session_state.exam_start_time = time.time()
                    st.session_state.exam_duration = minutes * 60
                else:
                    st.session_state.exam_start_time = None
                    st.session_state.exam_duration = None

        # Show exam
        if "exam_questions" in st.session_state and not st.session_state.get("exam_submitted", False):
            questions = st.session_state.exam_questions

            # Timer display
            if st.session_state.get("exam_start_time"):
                import time
                elapsed = time.time() - st.session_state.exam_start_time
                remaining = st.session_state.exam_duration - elapsed

                if remaining <= 0:
                    st.error("⏰ Time is up! Submitting exam...")
                    st.session_state.exam_submitted = True
                    st.rerun()
                else:
                    mins = int(remaining // 60)
                    secs = int(remaining % 60)
                    st.warning(f"⏱️ Time remaining: {mins:02d}:{secs:02d}")

            st.markdown("---")
            st.subheader(f"📝 {difficulty} Exam — {len(questions)} Questions")

            # Display questions
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}: {q.get('question', '')}**")
                options = q.get("options", [])
                if options:
                    choices = ["⬜ Not answered"] + options
                    selected = st.radio(
                        f"Select answer for Q{i+1}:",
                        choices,
                        key=f"exam_q_{i}",
                        label_visibility="collapsed"
                    )
                    if selected and selected != "⬜ Not answered":
                        st.session_state.exam_answers[i] = selected[0]
                    else:
                        st.session_state.exam_answers[i] = ""
                st.markdown("---")

            # Submit button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📤 Submit Exam", use_container_width=True):
                    st.session_state.exam_submitted = True
                    st.rerun()

        # Show results
        if st.session_state.get("exam_submitted") and "exam_questions" in st.session_state:
            questions = st.session_state.exam_questions
            answers = st.session_state.exam_answers

            # Calculate score
            score = 0
            for i, q in enumerate(questions):
                correct = q.get("answer", "").strip().upper()
                user_ans = answers.get(i, "").strip().upper()
                if user_ans == correct:
                    score += 1

            total = len(questions)
            percentage = round((score / total) * 100) if total > 0 else 0

            st.markdown("---")
            st.subheader("📊 Exam Results")

            # Score display
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{score}/{total}")
            with col2:
                st.metric("Percentage", f"{percentage}%")
            with col3:
                if percentage >= 80:
                    st.metric("Grade", "A 🌟")
                elif percentage >= 60:
                    st.metric("Grade", "B 👍")
                elif percentage >= 40:
                    st.metric("Grade", "C 📚")
                else:
                    st.metric("Grade", "F 💪")

            # Performance message
            if percentage >= 80:
                st.success("🌟 Excellent! You have mastered this topic!")
            elif percentage >= 60:
                st.info("👍 Good job! Review the wrong answers below.")
            elif percentage >= 40:
                st.warning("📚 Keep studying! Check the correct answers below.")
            else:
                st.error("💪 Don't give up! Review the material and try again.")

            st.markdown("---")
            st.subheader("📋 Answer Review")

            # Show each question with correct/wrong
            for i, q in enumerate(questions):
                correct = q.get("answer", "").strip().upper()
                user_ans = answers.get(i, "").strip().upper()
                is_correct = user_ans == correct

                if is_correct:
                    st.success(f"✅ Q{i+1}: {q.get('question', '')}")
                else:
                    st.error(f"❌ Q{i+1}: {q.get('question', '')}")
                    st.write(f"Your answer: **{user_ans}**")
                    st.write(f"Correct answer: **{correct}**")
                st.markdown("---")

            # Retry button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Retake Exam", use_container_width=True):
                    for key in ["exam_questions", "exam_answers",
                                "exam_submitted", "exam_text",
                                "exam_start_time", "exam_duration"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()

            # Download results
            result_text = f"Exam Results\nScore: {score}/{total} ({percentage}%)\n\n"
            for i, q in enumerate(questions):
                correct = q.get("answer", "").strip().upper()
                user_ans = answers.get(i, "").strip().upper()
                status = "✅" if user_ans == correct else "❌"
                result_text += f"{status} Q{i+1}: {q.get('question', '')}\n"
                result_text += f"Your answer: {user_ans} | Correct: {correct}\n\n"

            st.download_button(
                label="⬇️ Download Results",
                data=result_text,
                file_name="exam_results.txt",
                mime="text/plain"
            )
    # Tab:7 Voice Input
    with tab7:
        st.subheader(" Voice Input")
        st.write("Upload an audio file and get an AI answer!")

        st.info(" Record your question on your phone and upload here!")

        audio_file = st.file_uploader(
            "Upload your audio question",
            type=["wav", "mp3", "ogg", "flac"],
        )

        if audio_file:
            st.write(f"📄 File: {audio_file.name} | Size: {audio_file.size} bytes")
            st.info("ℹ️ Audio preview may not work for WhatsApp files — but transcription works perfectly!")

            if st.button(" Transcribe & Answer"):
                try:
                    import subprocess
                    import wave
                    import speech_recognition as sr

                    FFMPEG_PATH = r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin\ffmpeg.exe"
                    BASE_DIR = r"C:\Users\ELCOT\Documents\AI_STUDY_COPILOT"

                    ext = os.path.splitext(audio_file.name)[1].lower()
                    temp_input = os.path.join(BASE_DIR, f"temp_input{ext}")
                    temp_wav = os.path.join(BASE_DIR, "temp_output.wav")

                    # Step 1: Save uploaded file
                    with open(temp_input, "wb") as f:
                        f.write(audio_file.getbuffer())
                    st.write(f"✅ Step 1: Saved {os.path.getsize(temp_input)} bytes")

                    # Step 2: Convert to wav
                    if os.path.exists(temp_wav):
                        os.remove(temp_wav)

                    subprocess.run([
                        FFMPEG_PATH, "-y",
                        "-i", temp_input,
                        "-acodec", "pcm_s16le",
                        "-ar", "16000",
                        "-ac", "1",
                        "-f", "wav",
                        temp_wav
                    ], capture_output=True)

                    st.write(f"✅ Step 2: Converted {os.path.getsize(temp_wav)} bytes")

                    # Step 3: Transcribe
                    with wave.open(temp_wav, "rb") as w:
                        frames = w.readframes(w.getnframes())
                        rate = w.getframerate()

                    recognizer = sr.Recognizer()
                    audio_data = sr.AudioData(frames, rate, 2)

                    with st.spinner("Transcribing..."):
                        text = recognizer.recognize_google(audio_data)

                    st.write(f"✅ Step 3: Transcribed!")
                    st.success(f"🎤 You said: **{text}**")

                    # Cleanup
                    if os.path.exists(temp_input):
                        os.remove(temp_input)
                    if os.path.exists(temp_wav):
                        os.remove(temp_wav)

                    # Step 4: Get AI answer
                    with st.spinner("Getting answer..."):
                        results = search_pdf(vector_db, text)
                        answer = get_answer(text, results)

                    st.markdown("---")
                    st.subheader("💬 Answer:")
                    st.success(answer)

                    with st.expander("📄 View Sources"):
                        for i, source in enumerate(results):
                            st.markdown(f"**Chunk {i+1}:**")
                            st.info(source.page_content[:300] + "...")

                except Exception as e:
                    import traceback
                    st.error(f"❌ {str(e)}")
                    st.code(traceback.format_exc())

        st.markdown("---")
        st.subheader("⌨️ Or type your question:")

        voice_query = st.text_input(
            "Type your question here:",
            placeholder="Type your question...",
            key="voice_input"
        )

        if st.button(" Get Answer", use_container_width=True):
            if voice_query:
                with st.spinner("Thinking..."):
                    results = search_pdf(vector_db, voice_query)
                    answer = get_answer(voice_query, results)
                st.markdown("---")
                st.subheader("💬 Answer:")
                st.success(answer)
                with st.expander("📄 View Sources"):
                    for i, source in enumerate(results):
                        st.markdown(f"**Chunk {i+1}:**")
                        st.info(source.page_content[:300] + "...")
            else:
                st.warning(" Please type a question first!")
    