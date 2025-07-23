from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from unstructured.partition.pdf import partition_pdf
import uuid
import os
import shutil
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableMap

# --- Load env variables ---
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

# --- Partition PDF ---
def partition_my_docs(pdf_path="C:\\Users\\aravi\\Downloads\\Assignments\\W6D2\\data\\prime_alliance_mortgage_handbook_q3_2025.pdf"):
    if not os.path.exists(pdf_path):
        print(f"Error: The file was not found at {pdf_path}")
        return [], []

    elements = partition_pdf(
        filename=pdf_path,
        strategy="hi_res",
        infer_table_structure=True,
        chunking_strategy="by_title"
    )

    texts, tables = [], []
    for element in elements:
        if "unstructured.documents.elements.Table" in str(type(element)):
            tables.append(str(element))
        else:
            texts.append(str(element))
    return texts, tables

# --- Summarization Prompt ---
summarize_prompt = PromptTemplate.from_template("""
You are an assistant tasked with summarizing tables for a Retrieval Augmented Generation (RAG) system.
Give a concise summary of the table below. This summary will be used to decide whether to pull the full table for a user query.
Be precise about the type of data included.

Table:
{table}

Summary:""")

summarize_chain = (
    {"table": RunnablePassthrough()}
    | summarize_prompt
    | ChatOpenAI(model="gpt-4o-mini", max_retries=0)
    | StrOutputParser()
)

# --- Process and summarize docs ---
text_chunks, table_chunks = partition_my_docs()
table_summaries = summarize_chain.batch(table_chunks, {"max_concurrency": 5}) if table_chunks else []

doc_store = {}
summary_docs = []

for i, summary in enumerate(table_summaries):
    table_id = str(uuid.uuid4())
    doc_store[table_id] = table_chunks[i]
    summary_docs.append(Document(
        page_content=summary,
        metadata={"doc_id": table_id, "type": "table"}
    ))

text_docs = [Document(page_content=chunk, metadata={"type": "text"}) for chunk in text_chunks]
final_docs = summary_docs + text_docs

persist_directory = "./vector_store_advanced"

if final_docs:
    if os.path.exists(persist_directory):
        print(f"Removing existing vector store at '{persist_directory}' to avoid dimension conflicts.")
        shutil.rmtree(persist_directory)

    vectorstore_advanced = Chroma.from_documents(
        documents=final_docs,
        embedding=OpenAIEmbeddings(),
        persist_directory=persist_directory
    )
    retriever_advanced = vectorstore_advanced.as_retriever(search_kwargs={'k': 5})

    # --- Format retrieved docs ---
    def format_docs(docs):
        formatted = []
        for doc in docs:
            if doc.metadata.get("type") == "table":
                full_table = doc_store.get(doc.metadata.get("doc_id"), "Table not found.")
                formatted.append(f"--- Relevant Table ---\n{full_table}")
            else:
                formatted.append(doc.page_content)
        return "\n\n".join(formatted)

    # --- Prompt with history ---
    qa_prompt = PromptTemplate.from_template("""
You are a precise banking assistant. Answer the user's question based ONLY on the following context and chat history.
If unsure, say "I don't know."

Chat history:
{chat_history}

Context:
{context}

Question: {question}

Answer:
""")

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # --- Assembling the custom chain using LCEL ---
    def conversational_rag(question: str):
        retrieved_docs = retriever_advanced.invoke(question)
        context = format_docs(retrieved_docs)

        inputs = {
            "question": question,
            "context": context,
            "chat_history": memory.buffer_as_messages
        }

        response = (qa_prompt | llm | StrOutputParser()).invoke(inputs)

    # Save to memory
        memory.save_context({"question": question}, {"answer": response})

        return response


    # --- Start loop ---
    if __name__ == "__main__":
        print("\n--- Banking Assistant Ready ---")
        print("Enter 'quit' to exit.")

        while True:
            question = input("You: ")
            if question.lower() in ["quit", "exit"]:
                print("Assistant: Goodbye!")
                break

            answer = conversational_rag(question)
            print(f"Assistant: {answer}")

else:
    print("No documents were processed. Please check the PDF path and partitioning process.")
