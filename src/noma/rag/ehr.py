"""EHR (Electronic Health Records) Q&A with RAG."""

import gradio as gr
from PyPDF2 import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain


def create_knowledge_base(pdf_path: str):
    with open(pdf_path, "rb") as f:
        pdf_reader = PdfReader(f)
        text = "".join(page.extract_text() for page in pdf_reader.pages)

    splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)

    embeddings = OpenAIEmbeddings()
    return FAISS.from_texts(chunks, embeddings)


def _parse_chat_history(chat_history: str) -> list[tuple[str, str]]:
    history = []
    if not chat_history:
        return history

    for entry in chat_history.strip().split("\n\n"):
        lines = entry.strip().split("\n")
        if len(lines) >= 2:
            user_input = lines[0].replace("Surgeon: ", "").strip()
            assistant_response = lines[1].replace("Response: ", "").strip()
            history.append((user_input, assistant_response))
    return history


def _format_chat_history(chat_history: str) -> str:
    formatted = ""
    if not chat_history:
        return formatted

    for entry in chat_history.strip().split("\n\n"):
        lines = entry.strip().split("\n")
        if len(lines) >= 2:
            user_line = lines[0].replace("Surgeon: ", "").strip()
            response_line = lines[1].replace("Response: ", "").strip()
            formatted += f"<p><span class='surgeon'>Surgeon:</span> {user_line}</p>"
            formatted += f"<p><span class='response'>Response:</span> {response_line}</p>"
    return formatted


def create_ehr_app(pdf_path: str = "data/patient.pdf") -> gr.Blocks:
    knowledge_base = create_knowledge_base(pdf_path)

    def question_answer(question: str, chat_history: str) -> str:
        if not question.strip():
            return chat_history

        retriever = knowledge_base.as_retriever()
        llm = ChatOpenAI(model_name="gpt-4", temperature=0)
        qa_chain = ConversationalRetrievalChain.from_llm(llm, retriever=retriever)
        history = _parse_chat_history(chat_history)

        result = qa_chain.invoke({"question": question, "chat_history": history})
        response = result["answer"]

        return chat_history + f"Surgeon: {question}\nResponse: {response}\n\n"

    def updated_question_answer(question: str, chat_history: str):
        chat_history = question_answer(question, chat_history)
        formatted = _format_chat_history(chat_history)
        return gr.update(value=formatted), chat_history

    with gr.Blocks(css=_get_css()) as app:
        with gr.Column(elem_classes="container"):
            gr.Markdown(
                '<div class="title">EHR Querying</div>'
                '<div class="subtitle">Query EHR for potential complications</div>'
            )
            output = gr.HTML(label="Conversation", elem_id="chatbox")

            with gr.Row(elem_classes="input-row"):
                with gr.Column(elem_classes="wrap"):
                    question = gr.Textbox(
                        show_label=False,
                        placeholder="Type your question here...",
                        lines=1,
                        max_lines=1,
                    )
                btn = gr.Button("Send", variant="primary")

        state = gr.State("")
        btn.click(updated_question_answer, inputs=[question, state], outputs=[output, state])
        question.submit(updated_question_answer, inputs=[question, state], outputs=[output, state])

    return app


def _get_css() -> str:
    return """
    .container {max-width: 800px; margin: auto;}
    .title {text-align: center; font-size: 2em; font-weight: bold; margin-bottom: 10px;}
    .subtitle {text-align: center; font-size: 1em; color: gray; margin-bottom: 20px;}
    #chatbox {height: 400px; overflow-y: auto; background-color: #000; padding: 10px; border-radius: 5px;}
    #chatbox p {margin: 0 0 10px;}
    #chatbox .surgeon {color: #1f77b4; font-weight: bold;}
    #chatbox .response {color: #ff7f0e;}
    .input-row {display: flex; align-items: center; margin-top: 10px;}
    .input-row .wrap {flex-grow: 1;}
    .input-row textarea {width: 100%; resize: none;}
    .input-row button {margin-left: 10px;}
    """


def main():
    app = create_ehr_app()
    app.launch()


if __name__ == "__main__":
    main()

