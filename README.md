Here is the complete `README.md` file for your project.

-----

````markdown
# RAG for Banking Knowledge Base

This project is an advanced Retrieval-Augmented Generation (RAG) system built with LangChain. It serves as an AI assistant for a bank, answering questions about loan products, regulatory requirements, and internal policies from a document knowledge base.

## Key Features

- **Intelligent Document Processing:** Uses `unstructured.io` to parse complex PDFs, correctly identifying and separating narrative text from structured tables.
- **Advanced Table Handling:** Implements a multi-vector retrieval strategy. It creates summaries of tables for efficient searching but provides the full, original table to the LLM for context, solving the common "context loss" problem.
- **Conversational Memory:** The assistant can handle follow-up questions, remembering the context of the conversation.
- **Built for Evaluation:** Includes a modular evaluation script using the RAGAs framework to objectively measure performance on accuracy and faithfulness.

## Architecture Diagram

The system follows a sophisticated RAG pipeline designed for high-quality, context-aware responses.

````
<img width="1958" height="3840" alt="Untitled diagram _ Mermaid Chart-2025-07-23-100613" src="https://github.com/user-attachments/assets/98a8dab1-f8c2-4aa8-ac15-25a1b3e95c1f" />

````

## Setup & Usage

### Prerequisites

  - Python 3.9+
  - Poppler (for PDF processing on Windows/macOS)

### Installation

1.  Clone the repository:
    ```bash
    git clone <your-repo-link>
    cd <your-repo-folder>
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Assistant

1.  Place your PDF document in the `/data` directory.
2.  Create a `.env` file and add your OpenAI API key:
    ```
    OPENAI_API_KEY="sk-..."
    ```
3.  Run the main application:
    ```bash
    python main2.py
    ```
