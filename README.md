# Docmint AI Functionality Library 📘

Welcome to the Docmint AI Functionality Library readme! This library offers powerful AI-backed functionality to enhance your online documentation processes. With this library, you can generate mind maps in Markdown, optimize text content, manage knowledge databases, and even perform OCR (Optical Character Recognition) on images to extract text and create Markdown tables.

## Features 🌟

- **Mind Map Generation** (`/generate_mm`): Convert questions into structured mind maps in Markdown format.
- **Image Uploading** (`/upload_pic`): Upload and save images to a specific server directory.
- **Picture Generation** (`/generate_pic`): Generate images based on provided text content.
- **Text Optimization** (`/generate_TextOptimisation`): Enhance and optimize your text content.
- **Knowledge Base Management**:
  - Add documents to the knowledge base (`/knowledge_add_document`).
  - Ask questions and retrieve information from the knowledge base (`/knowledge_ask_question`).
  - Remove documents from the knowledge base (`/knowledge_remove_document`).
- **OCR Functionality**:
  - Convert image tables to Markdown format (`/to_markdown_table`).
  - Process images for OCR and retrieve text and images (`/ocr_process`).

## Requirements 🛠️

- Python 3.8 or higher.
- An internet connection to download and use Hugging Face models.

## Installation 📦

Clone the repository to your local machine:

```
git clone https://github.com/ychAlbert/docmint-AI-applications.git
```

Then you can run:

```
pip install -r requirement.txt
```


## Dependencies 📌

To ensure full functionality of the **AI-function-code-for-online-documentation**, we rely on a suite of packages. Below is an outline of our primary dependencies:

- **LangChain**: Our core dependency for managing knowledge bases, document loading, text splitting, and integrating machine learning models. 
 
    - `langchain.vectorstores.Chroma`
    - `langchain.document_loaders.PyMuPDFLoader, UnstructuredMarkdownLoader`
    - `langchain.text_splitter.RecursiveCharacterTextSplitter`
    - `langchain.embeddings.huggingface.HuggingFaceEmbeddings`
    - `langchain.chains.RetrievalQA`
    - `langchain.prompts.PromptTemplate`

- **dotenv**: For loading environment variables safely.


## Usage ✍️

1. **Run the Flask application**:

```python
from your_application_module import app

if __name__ == '__main__':
    app.run(debug=True)
```

2. **Interacting with API Endpoints**:

Use the following API endpoints for carrying out AI functionality:

### Mind Map Generation

**POST** `/generate_mm`  

```json
{
  "question": "Your question for mind map generation"
}
```

### Image Uploading

**POST** `/upload_pic`  

Form-data:
```
file: (binary file content)
```

### Picture Generation

**POST** `/generate_pic`  

```json
{
  "question": "Your question for picture generation"
}
```

### Text Optimization

**POST** `/generate_TextOptimisation`  

```json
{
  "question": "Your text content for optimization"
}
```

### Knowledge Base Management

Add Document:
**POST** `/knowledge_add_document`  

```json
{
  "document_path": "Path to your document"
}
```

Ask Question:
**POST** `/knowledge_ask_question`  

```json
{
  "question": "Your question to the knowledge base"
}
```

Remove Document:
**POST** `/knowledge_remove_document`  

```json
{
  "document_path": "Path to document to remove"
}
```

### OCR Functionality

Convert Image to Markdown Table:
**POST** `/to_markdown_table`  

Form-data:
```
file: (binary file content)
```

OCR Process Image:
**POST** `/ocr_process`  

Form-data:
```
file: (binary file content)
```

## File Upload Requirements 📂

When using endpoints that require file upload (`/upload_pic`, `/to_markdown_table`, `/ocr_process`), ensure the request contains a file part with the name 'file'.

## Error Handling ⚙️

In case of errors, such as missing file part or document path, the endpoints will return appropriate error messages and HTTP status codes.

## Contributions 🤝

We welcome contributions and suggestions to enhance this library. Feel free to fork the project and submit pull requests.

## Support 💭

For support on how to use the library or to report issues, please submit an issue on the project's issue tracker.

Thank you for choosing Docmint AI Functionality Library to empower your documentation processes!

---

With 🖤 by the Docmint developer community!
