from dotenv import load_dotenv
import gradio as gr
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback

load_dotenv()


# Pre-process the PDF and create the knowledge base
def create_knowledge_base(pdf_path):
    with open(pdf_path, "rb") as f:
        pdf_reader = PdfReader(f)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

    # Chunking
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=200
    )
    chunks = text_splitter.split_text(text)

    # Embeddings
    embeddings = OpenAIEmbeddings()
    knowledge_base = FAISS.from_texts(chunks, embeddings)

    return knowledge_base


# Load the knowledge base once at the start
knowledge_base = create_knowledge_base("patient.pdf")


# Function to handle user questions
def question_answer(question, chat_history):
    if not question.strip():
        return chat_history  # Return the chat_history string

    retriever = knowledge_base.as_retriever()

    # Initialize ChatOpenAI with the desired model
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)

    # Create a ConversationalRetrievalChain
    qa_chain = ConversationalRetrievalChain.from_llm(llm, retriever=retriever)

    # Parse existing chat history
    history = []
    if chat_history:
        entries = chat_history.strip().split("\n\n")
        for entry in entries:
            lines = entry.strip().split("\n")
            if len(lines) >= 2:
                user_input = lines[0].replace("Surgeon: ", "").strip()
                assistant_response = lines[1].replace("Response: ", "").strip()
                history.append((user_input, assistant_response))

    with get_openai_callback() as cb:
        result = qa_chain({"question": question, "chat_history": history})
        response = result["answer"]

    chat_history += f"Surgeon: {question}\nResponse: {response}\n\n"
    return chat_history  # Return the updated chat history string


# Build the Gradio app
# Build the Gradio app
with gr.Blocks(
    css="""
    .container {max-width: 800px; margin: auto;}
    .title {text-align: center; font-size: 2em; font-weight: bold; margin-bottom: 10px;}
    .subtitle {text-align: center; font-size: 1em; color: gray; margin-bottom: 20px;}
    #chatbox {height: 400px; overflow-y: auto; background-color: #000000; padding: 10px; border-radius: 5px;}
    #chatbox p {margin: 0 0 10px;}
    #chatbox .surgeon {color: #1f77b4; font-weight: bold;}
    #chatbox .response {color: #ff7f0e;}
    .input-row {display: flex; align-items: center; margin-top: 10px;}
    .input-row .wrap {flex-grow: 1;}
    .input-row textarea {width: 100%; resize: none;}
    .input-row button {margin-left: 10px;}
"""
) as demo:
    with gr.Column(elem_classes="container"):
        gr.Markdown(
            """
            <div class="title">🏥 EHR Querying</div>
            <div class="subtitle">Query EHR for potential complications</div>
            """
        )

        output = gr.HTML(
            label="Conversation",
            elem_id="chatbox",
        )

        with gr.Row(elem_classes="input-row"):
            with gr.Column(elem_classes="wrap"):
                question = gr.Textbox(
                    show_label=False,
                    placeholder="Type your question here...",
                    lines=1,
                    max_lines=1,
                )
            btn = gr.Button("Send", variant="primary")

    def format_chat_history(chat_history):
        formatted = ""
        if chat_history:
            entries = chat_history.strip().split("\n\n")
            for entry in entries:
                lines = entry.strip().split("\n")
                if len(lines) >= 2:
                    user_line = lines[0].replace("Surgeon: ", "").strip()
                    response_line = lines[1].replace("Response: ", "").strip()
                    formatted += (
                        f"<p><span class='surgeon'>Surgeon:</span> {user_line}</p>"
                    )
                    formatted += f"<p><span class='response'>Response:</span> {response_line}</p>"
        return formatted

    def updated_question_answer(question, chat_history):
        # Get the updated chat history string
        chat_history = question_answer(question, chat_history)
        # Format the chat history for HTML display
        formatted_history = format_chat_history(chat_history)
        # Update the output HTML component and return the new state
        return gr.update(value=formatted_history), chat_history

    state = gr.State("")
    btn.click(
        updated_question_answer, inputs=[question, state], outputs=[output, state]
    )
    question.submit(
        updated_question_answer, inputs=[question, state], outputs=[output, state]
    )

demo.launch()
