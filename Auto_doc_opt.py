import requests
import json
from typing import Any, Dict, List, Optional, Tuple, Union
import os
from dotenv import load_dotenv, find_dotenv
from wenxin_llm import Wenxin_LLM


# 读取Markdown文件内容
def read_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


# 将API响应写入Markdown文件
def write_to_markdown_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def Auto_doc_opt(file_path):
    FILE_PATH = file_path
    wenxin = Wenxin_LLM(access_token=os.environ["ERNIE_BOT_ACCESS_TOKEN"])
    formatting_request = "我将给你发送一篇完整的markdown文档，请帮助我将其根据文档内容（可能是论文、短文、信件等等）判断使用场景，根据其使用场景优化文本内容。我要求你不可以省略任何内容,并且不需要回答除了markdown以外的任何内容。你只需要给出完整的优化后文本:"
    original_content = read_markdown_file(FILE_PATH)  # 读取Markdown文件的内容
    combined_request = formatting_request + "\n\n" + original_content  # 将请求和原内容结合
    formatted_content = wenxin._call(combined_request)
    print(formatted_content)
    #write_to_markdown_file(FILE_PATH, formatted_content)
