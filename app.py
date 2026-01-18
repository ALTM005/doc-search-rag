import os
import streamlit as st
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Cassandra
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

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

    st.write(f"✅ File uploaded: {uploaded_file.name}")