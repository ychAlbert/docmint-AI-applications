import base64
import pathlib
import pprint
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


# 从环境变量中获取token
TOKEN = os.getenv('TOKEN')
API_URL = "https://90kdo913jag5aazd.aistudio-hub.baidu.com/ocr"


def encode_image_to_base64(image_path):
    """输入目标图片路径，返回Base64编码的图片字符串"""
    image_bytes = pathlib.Path(image_path).read_bytes()
    image_base64 = base64.b64encode(image_bytes).decode('ascii')
    return image_base64


def get_ocr_text_result(image_base64):
    """输入Base64编码的图片字符串，返回OCR文本结果"""
    # 设置鉴权信息
    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {"image": image_base64}  # Base64编码的文件内容或者文件链接
    resp = requests.post(url=API_URL, json=payload, headers=headers)
    assert resp.status_code == 200
    result = resp.json()["result"]
    pprint.pp(result["texts"])
    return result["texts"]


def get_ocr_image_result(image_base64, output_image_path):
    """输入Base64编码的图片字符串，输出OCR图像结果并保存图像"""
    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {"image": image_base64}
    resp = requests.post(url=API_URL, json=payload, headers=headers)
    assert resp.status_code == 200
    result = resp.json()["result"]

    with open(output_image_path, "wb") as f:
        f.write(base64.b64decode(result["image"]))
    print(f"OCR结果图保存在 {output_image_path}")
