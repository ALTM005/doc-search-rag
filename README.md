# 📄 DocSearch RAG (PDF Chatbot)

A Retrieval Augmented Generation (RAG) engine that allows users to chat with PDF documents using natural language. Built with the "Modern Data Stack": Astra DB (Vector Search), LangChain, and OpenAI.

## 🏗️ Architecture
* **Ingestion:** PDF documents are loaded and split into 400-token chunks.
* **Vector Store:** Chunks are embedded using OpenAI (`text-embedding-3-small`) and stored in **DataStax Astra DB** (Cassandra) for sub-millisecond retrieval.
* **Retrieval:** Hybrid search locates the top 3 most relevant context chunks.
* **Generation:** GPT-3.5 Turbo synthesizes the answer based *only* on the retrieved context to minimize hallucinations.

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **Orchestration:** LangChain v0.1
* **Database:** Astra DB Serverless (Cassandra Vector)
* **LLM:** OpenAI GPT-3.5 Turbo

## 🚀 How to Run
1.  Clone the repository
2.  Install dependencies: `pip install -r requirements.txt`
3.  Add your `bundle.zip` (Secure Connect Bundle) to the root directory.
4.  Run the app: `streamlit run app.py`