# 集成示例

将 Doctra 与其他工具和框架集成的示例。

## Flask Web 应用程序

```python
from flask import Flask, request, jsonify, send_file
from doctra import StructuredPDFParser
import os

app = Flask(__name__)
parser = StructuredPDFParser()

@app.route('/parse', methods=['POST'])
def parse_document():
    if 'file' not in request.files:
        return jsonify({'error': '未提供文件'}), 400
    
    file = request.files['file']
    
    # 保存上传的文件
    pdf_path = f"uploads/{file.filename}"
    file.save(pdf_path)
    
    # 解析文档
    try:
        parser.parse(pdf_path)
        return jsonify({
            'status': 'success',
            'output_dir': f"outputs/{file.filename.replace('.pdf', '')}"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
```

## FastAPI 服务

```python
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from doctra import StructuredPDFParser
import shutil

app = FastAPI()
parser = StructuredPDFParser()

@app.post("/parse")
async def parse_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    # 保存文件
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 排队处理
    background_tasks.add_task(parser.parse, file_path)
    
    return {"status": "processing", "filename": file.filename}
```

## 数据库集成

```python
from doctra import StructuredPDFParser
import sqlite3
import json

def store_results_in_db(pdf_path, db_path="documents.db"):
    # 解析文档
    from doctra.engines.vlm.service import VLMStructuredExtractor
    
    vlm_engine = VLMStructuredExtractor(
        vlm_provider="openai",
        api_key="your-api-key"
    )
    
    parser = StructuredPDFParser(vlm=vlm_engine)
    parser.parse(pdf_path)
    
    # 连接到数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            num_pages INTEGER,
            content TEXT,
            metadata TEXT
        )
    ''')
    
    # 加载结果
    result_path = f"outputs/{os.path.basename(pdf_path).replace('.pdf', '')}/full_parse/result.md"
    with open(result_path) as f:
        content = f.read()
    
    # 存储到数据库
    cursor.execute(
        "INSERT INTO documents (filename, content) VALUES (?, ?)",
        (pdf_path, content)
    )
    
    conn.commit()
    conn.close()
```

## AWS Lambda 函数

```python
import json
import boto3
from doctra import StructuredPDFParser

s3 = boto3.client('s3')
parser = StructuredPDFParser()

def lambda_handler(event, context):
    # 从 S3 获取 PDF
    bucket = event['bucket']
    key = event['key']
    
    # 下载文件
    local_path = f"/tmp/{key}"
    s3.download_file(bucket, key, local_path)
    
    # 解析文档
    parser.parse(local_path, output_base_dir="/tmp/outputs")
    
    # 将结果上传回 S3
    output_dir = f"/tmp/outputs/{key.replace('.pdf', '')}"
    # ... 上传逻辑 ...
    
    return {
        'statusCode': 200,
        'body': json.dumps('处理完成')
    }
```

## 另请参阅

- [基本示例](basic-usage.md) - 入门
- [高级示例](advanced-examples.md) - 复杂模式
- [API 参考](../api/parsers.md) - API 文档

