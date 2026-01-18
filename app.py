import os
import streamlit as st
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain.indexes import VectorStoreIndexCreator
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Cassandra
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

st.set_page_config(page_title="Chat with PDF", page_icon="📄")
st.title("📄 Chat with PDF")

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