import os
from dotenv import load_dotenv, find_dotenv
from wenxin_llm import Wenxin_LLM

def MM_generation(question):
    wenxin = Wenxin_LLM(access_token=os.environ["ERNIE_BOT_ACCESS_TOKEN"])
    formatting_request = "我要求你扮演思维导图生成器，我会给你一个主题，你将使用Markdown格式（代码块）写下关于这个主题的思维导图。我要求你不可以省略任何内容,并且不需要回答除了markdown以外的任何内容。:"
    original_content = question
    combined_request = formatting_request + "\n\n" + original_content  # 将请求和原内容结合
    formatted_content = wenxin._call(combined_request)
    print(formatted_content)
