import gradio as gr
import openai
import os
from docx import Document
import PyPDF2

openai.api_key = os.getenv("GROQ_API_KEY")
openai.api_base = "https://api.groq.com/openai/v1"


def extract_text(file_path):
    text = ""

    if file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    return text.strip()

def process_doc(file_path, target_language):
    if not file_path:
        return ["⚠️ Please upload a file."] * 5

    content = extract_text(file_path)

    if not content:
        return ["⚠️ File is empty or unreadable."] * 5

    prompts = [
        f"Summarize this:\n{content}",
        f"List key points:\n{content}",
        f"Extract and define important terms:\n{content}",
        f"Generate exam/quiz questions:\n{content}",
        f"Translate into {target_language}:\n{content}"
    ]

    outputs = []

    for prompt in prompts:
        try:
            response = openai.ChatCompletion.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            outputs.append(response.choices[0].message.content.strip())
        except Exception as e:
            outputs.append(f"❌ Error: {e}")

    return outputs

with gr.Blocks(css="""
    .gr-textbox textarea { background-color: #fff8f0 !important; font-size: 16px; }
    .gr-button { background: linear-gradient(45deg, #ff9a9e, #fad0c4) !important; font-weight: bold; }
""") as demo:

    gr.Markdown("## 🌟 AI Study Assistant")

    with gr.Row():
        file_input = gr.File(label="📂 Upload PDF or DOCX", file_types=[".pdf", ".docx"])
        lang_input = gr.Textbox(label="🌍 Translate to", placeholder="Tamil / Hindi / French")

    btn = gr.Button("🚀 Generate")

    with gr.Row():
        summary = gr.Textbox(label="📘 Summary")
        points = gr.Textbox(label="✅ Key Points")

    with gr.Row():
        defs = gr.Textbox(label="📚 Definitions")
        questions = gr.Textbox(label="❓ Questions")
        translation = gr.Textbox(label="🌐 Translation")

    btn.click(
        fn=process_doc,
        inputs=[file_input, lang_input],
        outputs=[summary, points, defs, questions, translation]
    )

demo.launch()