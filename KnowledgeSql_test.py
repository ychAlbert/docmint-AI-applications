from KnowledgeSql import DocumentKnowledgeRetriever
knowledge_retriever = DocumentKnowledgeRetriever()
knowledge_retriever.add_document_path("data_base/knowledge_db/1.md")
question = "详细讲解一下本知识库的内容"
response, documents = knowledge_retriever.ask_question(question)
# 动态删除文档路径
knowledge_retriever.remove_document_path("data_base/knowledge_db/pumpkin_book.pdf")

# 再次提出问题，将不包括已删除文档的内容
response, documents = knowledge_retriever.ask_question(question)