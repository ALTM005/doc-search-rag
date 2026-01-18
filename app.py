import os
import streamlit as st
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Cassandra
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

st.set_page_config(page_title="Chat with PDF", page_icon="📄")

with st.sidebar:
    st.header("🔑 Configuration")
    OPENAI_API_KEY = st.text_input("OpenAI API Key", type="password")
    ASTRA_DB_TOKEN = st.text_input("Astra DB Token (AstraCS...)", type="password")
    ASTRA_DB_BUNDLE_PATH = st.text_input("Path to Bundle.zip", value="bundle.zip")
    ASTRA_DB_KEYSPACE = st.text_input("Keyspace Name", value="default_keyspace")

if not OPENAI_API_KEY or not ASTRA_DB_TOKEN:
    st.info("Please add your API keys in the sidebar to continue.")
    st.stop()

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

@st.cache_resource
def get_astra_session(token, bundle_path):
    cloud_config = {'secure_connect_bundle': bundle_path}
    auth_provider = PlainTextAuthProvider('token', token)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    return session

try:
    session = get_astra_session(ASTRA_DB_TOKEN, ASTRA_DB_BUNDLE_PATH)
except Exception as e:
    st.error(f"❌ Connection Failed: {e}")
    st.stop()

st.title("📄 Chat with PDF")

if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file:
    temp_path = f"./temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if "vectorstore" not in st.session_state:
        with st.spinner("🧠 Indexing document... this might take a moment"):
            
            # Load the PDF
            loader = PyPDFLoader(temp_path)
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=30)
            splits = splitter.split_documents(docs)

            vectorstore = Cassandra.from_documents(
                documents=splits,
                embedding=OpenAIEmbeddings(),
                session=session,
                keyspace=ASTRA_DB_KEYSPACE,
                table_name='pdf_chat_history', 
            )

            st.session_state.vectorstore = vectorstore
            st.success("✅ Document Indexed! You can now ask questions.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about the PDF..."):
        # Display user message immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if "vectorstore" in st.session_state:
                    retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})
                    
                    qa_chain = RetrievalQA.from_chain_type(
                        llm=ChatOpenAI(temperature=0.1), 
                        chain_type="stuff", 
                        retriever=retriever
                    )
                    
                    response = qa_chain.run(prompt)
                else:
                    response = "⚠️ Please upload a PDF first to start chatting!"
                
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Cleanup temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)