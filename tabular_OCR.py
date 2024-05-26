import os
from dotenv import load_dotenv
import base64
import pathlib
import pprint
import requests

# 加载.env文件中的环境变量
load_dotenv()

# 从环境变量中获取token
TOKEN = os.getenv('ERNIE_BOT_ACCESS_TOKEN')
API_URL = "https://b43cm9sfi7v9k520.aistudio-hub.baidu.com/table-recognition"


def encode_and_send_image(image_path):
    """
    输入本地图片路径，发送请求并获得OCR结果
    """
    # 对本地图片进行Base64编码
    image_bytes = pathlib.Path(image_path).read_bytes()
    image_base64 = base64.b64encode(image_bytes).decode('ascii')

    # 设置鉴权信息
    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json"
    }

    # 设置请求体
    payload = {
        "image": image_base64  # Base64编码的文件内容或者文件链接
    }

    # 调用
    resp = requests.post(url=API_URL, json=payload, headers=headers)

    # 处理接口返回数据
    assert resp.status_code == 200
    result = resp.json()["result"]
    pprint.pp(result["tables"])

    return result["tables"]


def convert_html_to_markdown(html_content):
    """
    将HTML表格内容转换为Markdown形式的表格
    """
    table_rows = html_content.split('<tr>')[1:]  # 分割出所有行，去掉首个空元素
    markdown_table = ""

    # 构建Markdown表格的表头
    header_row = table_rows.pop(0).split('</td><td>')  # 处理第一行为表头
    header_row = [cell.replace('<td>', '').replace('</td>', '').strip() for cell in header_row]  # 清理每个单元格内容
    markdown_table += "| " + " | ".join(header_row) + " |\n"
    markdown_table += "|-" + "-|".join(["---" for _ in header_row]) + "-|\n"

    # 构建Markdown表格的主体
    for row in table_rows:
        cells = row.split('</td><td>')  # 分割单元格
        cells = [cell.replace('<td>', '').replace('</td>', '').strip() for cell in cells]  # 清理每个单元格内容
        markdown_row = "| " + " | ".join(cells) + " |\n"
        markdown_table += markdown_row

    return markdown_table

