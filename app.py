import hashlib
import json
from flask import Flask, render_template, request, jsonify, make_response, send_from_directory, current_app
import os
from OCR import get_ocr_text_result
from OCR import get_ocr_image_result
from OCR import encode_image_to_base64
from tabular_OCR import encode_and_send_image
from tabular_OCR import convert_html_to_markdown
from KnowledgeSql import DocumentKnowledgeRetriever

knowledge_retriever = DocumentKnowledgeRetriever()
from werkzeug.utils import secure_filename

from wenxin_llm import Wenxin_LLM

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/imgs'  # 替换为你的上传文件夹路径
app.config['OUTPUT_FOLDER'] = '/imgs'  # 替换为你的输出文件夹路径


def MM_generation(question):
    wenxin = Wenxin_LLM(access_token=os.environ["ERNIE_BOT_ACCESS_TOKEN"])
    formatting_request = "我要求你扮演思维导图生成器，我会给你一个主题，你将使用Markdown格式（代码块）写下关于这个主题的思维导图。我要求你不可以省略任何内容,并且不需要回答除了markdown以外的任何内容。:"
    combined_request = formatting_request + "\n\n" + question  # 将请求和原内容结合
    formatted_content = wenxin._call(combined_request)
    print(formatted_content)
    return formatted_content

#
def pic_generation(question):
    wenxin = Wenxin_LLM(access_token=os.environ["ERNIE_BOT_ACCESS_TOKEN"])
    formatting_request = "我要求你扮演图像生成器，我会给你一个主题，你将使用Markdown格式（代码块）写下关于这个主题的图像。我要求你不可以省略任何内容,并且不需要回答除了markdown以外的任何内容.:"
    combined_request = formatting_request + "\n\n" + question  # 将请求和原内容结合
    formatted_content = wenxin._call(combined_request)
    print(formatted_content)
    return formatted_content


def TextOptimisation(question):
    wenxin = Wenxin_LLM(access_token=os.environ["ERNIE_BOT_ACCESS_TOKEN"])
    formatting_request = "我要求你扮演文本优化器，我会给你一段文本，我需要你自行判断这段文本的使用场景，并根据场景给出优化后的文本。我要求你不可以省略任何内容,并且不需要回答除了文本以外的任何内容.:"
    combined_request = formatting_request + "\n\n" + question  # 将请求和原内容结合
    formatted_content = wenxin._call(combined_request)
    print(formatted_content)
    return formatted_content


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate_mm', methods=['POST'])
# 这里是处理前端发送的POST请求,生成思维导图的markdown格式
def generate_mm():
    question = request.form['question']
    response = MM_generation(question)
    return jsonify({"response": response})


@app.route('/upload_pic', methods=['POST'])
# 这里是处理前端发送的POST请求,上传图片并保存到imgs文件夹中
def upload_pic():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:  # 这里可以加文件类型判断逻辑
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200


@app.route('/generate_pic', methods=['POST'])
# 这里是处理前端发送的POST请求,文生图（还未实现）
def generate_pic():
    question = request.form['question']
    response = pic_generation(question)
    return jsonify({"response": response})


@app.route('/generate_TextOptimisation', methods=['POST'])
# 这里是处理前端发送的POST请求,文本优化
def generate_TextOptimisation():
    question = request.form['question']
    response = TextOptimisation(question)
    return jsonify({"response": response})


'''知识库接口'''


# 当请求中提供了有效的'document_path'时，接口会将信息"Document path added successfully."以及状态码200作为响应返回。
# 当请求中未提供'document_path'时，接口会将错误信息"No document path provided."以及状态码400作为响应返回。
@app.route('/knowledge_add_document', methods=['POST'])  # 添加知识库文档
def add_document():
    document_path = request.json.get('document_path', '')
    if document_path:
        knowledge_retriever.add_document_path(document_path)
        return jsonify({"message": "Document path added successfully."}), 200
    else:
        return jsonify({"error": "No document path provided."}), 400


# 当请求中提供了有效的'question'时，接口会调用knowledge_retriever.ask_question(question)方法，获取问答的结果和相关文档，并将其以JSON形式返回，状态码为200。
# 当请求中未提供'question'时，接口会返回错误信息"No question provided."，并将状态码设为400。
@app.route('/knowledge_ask_question', methods=['POST'])  # 对知识库问答
def ask_question():
    question = request.json.get('question', '')
    if question:
        response, documents = knowledge_retriever.ask_question(question)
        return jsonify({"response": response, "documents": documents}), 200
    else:
        return jsonify({"error": "No question provided."}), 400


@app.route('/knowledge_remove_document', methods=['POST'])  # 删除知识库文档
def remove_document():
    document_path = request.json.get('document_path', '')
    if document_path:
        knowledge_retriever.remove_document_path(document_path)
        return jsonify({"message": "Document path removed successfully."}), 200
    else:
        return jsonify({"error": "No document path provided."}), 400


'''OCR接口'''


# 识别图片表格
# 这个接口的返回值是一个JSON对象，包含一个名为'markdown_table'的字段，其中包含了转换后的Markdown表格内容
@app.route('/to_markdown_table', methods=['POST'])
def convert_to_markdown_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)
        ocr_result = encode_and_send_image(image_path)
        html_content = ocr_result[0]['html']
        markdown_table = convert_html_to_markdown(html_content)
        return jsonify({'markdown_table': markdown_table})


# 这个接口的返回值是一个JSON对象，包含了OCR识别后的文本信息
@app.route('/ocr_process', methods=['POST'])
def ocr_process_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)
        image_base64 = encode_image_to_base64(image_path)  # 这里假设你有这个实现
        ocr_texts = get_ocr_text_result(image_base64)
        output_image_path = os.path.join(app.config['OUTPUT_FOLDER'], file.filename)  # 输出图片路径
        get_ocr_image_result(image_base64, output_image_path)
        response_data = {
            'text_info': ocr_texts
        }
        return jsonify(response_data), 200, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run(debug=True)
# 运行flask
