'''
def wenxin_embedding(text: str):
    # 获取环境变量 wenxin_api_key、wenxin_secret_key
    api_key = os.environ['QIANFAN_AK']
    secret_key = os.environ['QIANFAN_SK']

    # 使用API Key、Secret Key向https://aip.baidubce.com/oauth/2.0/token 获取Access token
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={0}&client_secret={1}".format(api_key, secret_key)
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    # 通过获取的Access token 来embedding text
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings/embedding-v1?access_token=" + str(response.json().get("access_token"))
    input = []
    input.append(text)
    payload = json.dumps({
        "input": input
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return json.loads(response.text)
    '''

from langchain.vectorstores import Chroma
from langchain.document_loaders import PyMuPDFLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_embedding_ErnieBotSDK import ErnieEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import numpy as np
import erniebot
import requests
import json
import os
from dotenv import load_dotenv, find_dotenv

erniebot.api_type = 'aistudio'
load_dotenv()
erniebot.access_token = os.getenv('ERNIE_BOT_ACCESS_TOKEN')


class DocumentKnowledgeRetriever:
    _ = load_dotenv(find_dotenv())
    model_name = 'ernie-text-embedding'  # 文心一言的模型名称

    def __init__(self, model_name="moka-ai/m3e-base", vector_db_path='data_base/vector_db/chroma'):
        self.document_paths = []  # 初始化为空列表
        self.model_name = model_name
        self.vector_db_path = vector_db_path
        self.setup_environment()
        self.docs = []
        self.vectordb = None
        self.llm = self.setup_llm()
        self.qa_chain = None

    def setup_environment(self):
        os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
        os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

    def add_document_path(self, path):
        """添加文档路径到列表"""
        self.document_paths.append(path)
        self.docs.extend(self.load_documents([path]))
        self.vectordb = self.setup_vectordb()  # 重新设置vectordb以包含新文档
        self.qa_chain = self.setup_qa_chain()  # 重新创建qa_chain

    def remove_document_path(self, path):
        """删除文档路径从列表"""
        if path in self.document_paths:
            self.document_paths.remove(path)
            self.docs = self.load_documents(self.document_paths)  # 重新加载现有文档
            self.vectordb = self.setup_vectordb()  # 重新设置vectordb以移除文档
            self.qa_chain = self.setup_qa_chain()  # 重新创建qa_chain

    def load_documents(self, paths=None):
        """加载给定路径的文档，如果没有给定，则加载所有已知路径的文档"""
        if paths is None:
            paths = self.document_paths
        loaders = [PyMuPDFLoader(path) if path.endswith('.pdf') else UnstructuredMarkdownLoader(path) for path in paths]
        docs = []
        for loader in loaders:
            docs.extend(loader.load())
        return docs

    def setup_vectordb(self):
        # 切分文档
        ernieChunkSize = 384
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=ernieChunkSize, chunk_overlap=0)
        split_docs = text_splitter.split_documents(self.docs)
        # 定义 Embeddings 和 Vector 数据库
        # embedding = HuggingFaceEmbeddings(model_name=self.model_name)
        embedding = ErnieEmbeddings(access_token=erniebot.access_token)
        vectordb = Chroma.from_documents(
            documents=split_docs[:100],
            embedding=embedding,
            persist_directory=self.vector_db_path
        )
        vectordb.persist()
        vectordb = Chroma(persist_directory=self.vector_db_path, embedding_function=embedding)
        return vectordb

    def setup_llm(self):
        from wenxin_llm import Wenxin_LLM
        llm = Wenxin_LLM(access_token=os.environ["ERNIE_BOT_ACCESS_TOKEN"])
        return llm

    def setup_qa_chain(self):
        template = """以下上下文片段是用户构建的知识库内容，请使用其来回答最后的问题。如果你不知道答案，只需说不知道，不要试图编造答案。你只需要回答和知识库相关的内容，不需要回答其他任何内容。"
        {context}
        问题：{question}
        有用的回答："""
        QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

        qa_chain = RetrievalQA.from_chain_type(
            self.llm,
            retriever=self.vectordb.as_retriever(),
            return_source_documents=True,
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
        )
        return qa_chain

    def get_answer_from_result(self, result):
        """获取并显示大模型的回答"""
        answer = result.get('result')
        print(f"LLM 对问题的回答：{answer}")
        return answer

    def get_retrieved_documents_from_result(self, result):
        """获取并显示检索到的相关信息"""
        source_documents = result.get('source_documents', [])
        if source_documents:
            print(f"向量数据库检索到的最相关的文档：{source_documents[0]}")
        return source_documents

    def ask_question(self, question):
        """提交问题并获取大模型的回答和检索到的相关信息"""
        result = self.qa_chain({"query": question})
        answer = self.get_answer_from_result(result)
        source_documents = self.get_retrieved_documents_from_result(result)
        return answer, source_documents
