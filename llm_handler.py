from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_balanced_chunks(chunks, num_chunks=8, pdf_chunk_map=None):
    """Pick chunks evenly from EACH PDF separately"""
    
    # If we know which chunks belong to which PDF
    if pdf_chunk_map and len(pdf_chunk_map) > 1:
        selected = []
        per_pdf = max(2, num_chunks // len(pdf_chunk_map))
        
        for pdf_name, pdf_chunks in pdf_chunk_map.items():
            if len(pdf_chunks) <= per_pdf:
                selected.extend(pdf_chunks)
            else:
                step = len(pdf_chunks) // per_pdf
                picked = [pdf_chunks[i] for i in range(0, len(pdf_chunks), step)]
                selected.extend(picked[:per_pdf])
        
        return selected[:num_chunks]
    
    # Single PDF fallback
    if len(chunks) <= num_chunks:
        return chunks
    step = len(chunks) // num_chunks
    balanced = [chunks[i] for i in range(0, len(chunks), step)]
    return balanced[:num_chunks]


def get_answer(query, context_chunks):
    context = "\n\n".join([chunk.page_content for chunk in context_chunks])

    prompt = f"""You are a helpful study assistant. 
Answer the student's question using ONLY the context provided below.
If the answer is not in the context, say "I couldn't find that in the document."

Context:
{context}

Student's Question: {query}

Give a clear, easy-to-understand answer."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    return response.choices[0].message.content


def generate_quiz(chunks, num_questions=5, pdf_chunk_map=None):
    selected = get_balanced_chunks(chunks, num_chunks=8, pdf_chunk_map=pdf_chunk_map)
    context = "\n\n".join(selected)

    prompt = f"""You are a quiz generator. Based on the study material below, generate {num_questions} multiple choice questions.

Format your response EXACTLY like this for each question:
Q1: [Question here]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Answer: [Correct letter]
Explanation: [Why this is correct]

---

Study Material:
{context}

Generate exactly {num_questions} questions now:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    return response.choices[0].message.content


def generate_flashcards(chunks, num_cards=10, pdf_chunk_map=None):
    selected = get_balanced_chunks(chunks, num_chunks=8, pdf_chunk_map=pdf_chunk_map)
    context = "\n\n".join(selected)

    prompt = f"""You are a flashcard generator. Based on the study material below, generate {num_cards} flashcards.

Format EXACTLY like this for each flashcard:
CARD: [number]
FRONT: [Question or concept]
BACK: [Answer or explanation]
---

Study Material:
{context}

Generate exactly {num_cards} flashcards now:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    return response.choices[0].message.content


def generate_summary(chunks, pdf_chunk_map=None):
    selected = get_balanced_chunks(chunks, num_chunks=6, pdf_chunk_map=pdf_chunk_map)
    context = "\n\n".join(selected)

    prompt = f"""You are a study assistant. Summarize the study material below clearly.

Format your response EXACTLY like this:

📌 OVERVIEW:
[2-3 sentence overview of the entire document]

🔑 KEY TOPICS:
1. [Topic 1]
2. [Topic 2]
3. [Topic 3]
4. [Topic 4]
5. [Topic 5]

📝 MAIN POINTS:
- [Important point 1]
- [Important point 2]
- [Important point 3]
- [Important point 4]
- [Important point 5]

💡 KEY TERMS:
- [Term 1]: [Definition]
- [Term 2]: [Definition]
- [Term 3]: [Definition]

⭐ CONCLUSION:
[1-2 sentence conclusion]

Study Material:
{context}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    return response.choices[0].message.content


def socratic_tutor(query, context_chunks):
    context = "\n\n".join([chunk.page_content for chunk in context_chunks])

    prompt = f"""You are a Socratic tutor. Your job is to help students THINK, not just give answers.

RULES:
- NEVER give the direct answer
- Ask 2-3 guiding questions that lead the student to figure it out themselves
- Be encouraging and friendly
- Use hints from the context below

Context:
{context}

Student's Question: {query}

Respond with guiding questions only:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    return response.choices[0].message.content


def generate_exam(chunks, num_questions=10, difficulty="Medium", pdf_chunk_map=None):
    selected = get_balanced_chunks(chunks, num_chunks=10, pdf_chunk_map=pdf_chunk_map)
    context = "\n\n".join(selected)

    prompt = f"""You are an exam creator. Create a {difficulty} difficulty exam with {num_questions} questions.

Format EXACTLY like this for each question:
Q1: [Question]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
ANSWER: [Correct letter only, e.g. A]
---

Study Material:
{context}

Generate exactly {num_questions} questions now:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    return response.choices[0].message.content