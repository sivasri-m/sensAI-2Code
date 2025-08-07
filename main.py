# 📦 Make sure to install these packages first:
# pip install pymupdf openai

import fitz
import json
import openai
import os

# --- CONFIGURATION ---
# Replace with your actual API key
OPENAI_API_KEY = "sk-kpDEqImErpOsfeUvO-JP8A"
# HyperVerge LLM Gateway URL
OPENAI_BASE_URL = "https://agent.dev.hyperverge.org"

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
)

def extract_structured_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc, start=1):
        lines = []
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                line_text = " ".join([span["text"] for span in line["spans"]]).strip()
                if line_text:
                    lines.append({"text": line_text, "line_num": len(lines)+1})
        pages.append({"page_num": page_num, "lines": lines})

    return pages

def smart_chunk(pages, max_tokens=1500):
    chunks, current = [], ""
    token_estimate = lambda t: len(t.split())

    for page in pages:
        for line in page["lines"]:
            if token_estimate(current) > max_tokens:
                chunks.append(current.strip())
                current = ""
            current += f"{line['text']} "
    if current:
        chunks.append(current.strip())
    return chunks

def generate_questions(text, page_num=None):
    prompt = f"""
From the following educational document (page {page_num}), generate **1 question** (MCQ or SAQ) that checks key understanding.

Also include:
- question type ("MCQ" or "SAQ")
- options (if MCQ)
- correct answer
- citation (Page and Line if possible)

Text:
\"\"\"
{text}
\"\"\"

Respond in this JSON format:
{{
  "question": "...",
  "type": "MCQ or SAQ",
  "options": ["A", "B", "C", "D"],  # only if MCQ
  "answer": "...",
  "citation": "Page X, Line Y"
}}
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content.strip()
        return json.loads(content)

    except Exception as e:
        print(f"❌ Error generating question: {e}")
        return None

def mvp_full_processing(pdf_path):
    pages = extract_structured_text(pdf_path)
    full_text = " ".join(line["text"] for p in pages for line in p["lines"])

    if len(full_text.split()) < 120_000:
        # Small doc: generate 10 questions directly
        return [generate_questions(full_text, page_num=1) for _ in range(10)]

    else:
        # Large doc: chunk and generate 1 question per chunk
        chunks = smart_chunk(pages)
        questions = []

        for i, chunk in enumerate(chunks):
            q = generate_questions(chunk, page_num=i+1)
            if q:
                questions.append(q)

        return questions[:10]  # Return top 10

def save_questions_to_file(questions, output_path="questions.json"):
    with open(output_path, "w") as f:
        json.dump(questions, f, indent=2)

if __name__ == "__main__":
    pdf_path = input("Please enter the path to the PDF file: ").strip()

    if not os.path.isfile(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        exit(1)

    questions = mvp_full_processing(pdf_path)
    save_questions_to_file(questions)
    print("✅ Questions generated and saved to questions.json")
