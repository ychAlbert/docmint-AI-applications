import requests
from OCR import get_ocr_text_result
from OCR import get_ocr_image_result
from OCR import encode_image_to_base64
from tabular_OCR import encode_and_send_image
from tabular_OCR import convert_html_to_markdown


image_path = "./picture/test_tabular.png"
ocr_result = encode_and_send_image(image_path)
html_content = ocr_result[0]['html']
markdown_table = convert_html_to_markdown(html_content)
print(markdown_table)


image_path = "./picture/test_tabular.png"
output_image_path = "output.jpg"
image_base64 = encode_image_to_base64(image_path)
print("文本信息：")
ocr_texts = get_ocr_text_result(image_base64)
print("OCR图片处理...")
get_ocr_image_result(image_base64, output_image_path)