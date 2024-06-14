import json
import os
import sys
import boto3
import streamlit as st
from data_handlers.input_handlers import FileHandlerFactory

## We will be suing Titan Embeddings Model To generate Embedding

from langchain_community.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock

## Data Ingestion

import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader

# Vector Embedding And Vector Store

from langchain.vectorstores import FAISS

## LLm Models
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# file factory 
file_factory = FileHandlerFactory()

# get access keys from env variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')

## Bedrock Clients
bedrock=boto3.client(service_name="bedrock-runtime", region_name= "us-east-1", 
                     aws_access_key_id=AWS_ACCESS_KEY_ID,
                     aws_secret_access_key=AWS_SECRET_KEY)
bedrock_embeddings=BedrockEmbeddings(model_id="amazon.titan-embed-text-v1",client=bedrock)


## Data ingestion
def data_ingestion(pdffile):
    text_aggregated = ""
    for f in pdffile:
        types = f.type
        handler = file_factory.get_file_handler(types)
        txt = handler.read_file(f)
        text_aggregated += txt
    # loader=PyPDFDirectoryLoader(text_aggregated)
    # documents=loader.load()

    # - in our testing Character split works better with this PDF data set
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,
                                                 chunk_overlap=150,
                                                 separators=[" ", ",", "\n"])
    
    docs=text_splitter.split_text(text_aggregated)
    return docs

## Vector Embedding and vector store
def get_vector_store(docs):
    vectorstore_faiss=FAISS.from_texts(
        docs,
        bedrock_embeddings
    )
    vectorstore_faiss.save_local("faiss_index")


def get_llama2_llm():
    ##create the Anthropic Model
    llm=Bedrock(model_id="meta.llama2-70b-chat-v1",client=bedrock,
                model_kwargs={'max_gen_len':2048})
    
    return llm

prompt_template = """

Human: Use the following pieces of context to provide a 
concise answer to the question at the end but usse atleast summarize with 
250 words with detailed explaantions. If you don't know the answer, 
just say that you don't know, don't try to make up an answer.
<context>
{context}
</context

Question: {question}

Assistant:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

def get_response_llm(llm,vectorstore_faiss,query):
    qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore_faiss.as_retriever(
        search_type="similarity", search_kwargs={"k": 3}
    ),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)
    answer=qa({"query":query})
    return answer['result']



st.set_page_config("Chat PDF")

st.header("Chat with PDFs :books:")
pdffile = st.file_uploader("Upload your PDFs here:", type="pdf", accept_multiple_files=True)
st.write("Click :blue['Vectors Update'] on the right side of the screen once files are uploaded!")
user_question = st.text_input("Ask a Question from the PDF Files")

with st.sidebar:
    st.write("Update Or Create Vector Store:")
    
    if st.button("Vectors Update"):
        with st.spinner("Processing..."):
            docs = data_ingestion(pdffile)
            get_vector_store(docs)
            st.success("Done")


if st.button("Llama2 Output"):
    with st.spinner("Processing..."):
        faiss_index = FAISS.load_local("faiss_index", bedrock_embeddings, allow_dangerous_deserialization=True)
        llm=get_llama2_llm()
        
        #faiss_index = get_vector_store(docs)
        st.write(get_response_llm(llm,faiss_index,user_question))
        st.success("Done")
        
st.divider()

st.header("How it works?")
st.write("The chatbot is consisted of two parts: ")
st.write("1. The knoweledge base loader - it takes pdfs, reads them, splits into chunks, :blue[creates embeddings] (using :blue[Amazon Titan]) and puts to vector store.")
st.write("2. Designed prompt takes user query together with provided context (which is consisted of most similar (by default 3) chunks of text from vector store) and inputs to :blue[LLAMA2].")













