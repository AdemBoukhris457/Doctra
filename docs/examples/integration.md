# Integration Examples

Examples of integrating Doctra with other tools and frameworks.

## Flask Web Application

```python
from flask import Flask, request, jsonify, send_file
from doctra import StructuredPDFParser
import os

app = Flask(__name__)
parser = StructuredPDFParser()

@app.route('/parse', methods=['POST'])
def parse_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Save uploaded file
    pdf_path = f"uploads/{file.filename}"
    file.save(pdf_path)
    
    # Parse document
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

## FastAPI Service

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
    # Save file
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Queue processing
    background_tasks.add_task(parser.parse, file_path)
    
    return {"status": "processing", "filename": file.filename}
```

## Database Integration

```python
from doctra import StructuredPDFParser
import sqlite3
import json

def store_results_in_db(pdf_path, db_path="documents.db"):
    # Parse document
    parser = StructuredPDFParser(use_vlm=True)
    parser.parse(pdf_path)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            num_pages INTEGER,
            content TEXT,
            metadata TEXT
        )
    ''')
    
    # Load results
    result_path = f"outputs/{os.path.basename(pdf_path).replace('.pdf', '')}/full_parse/result.md"
    with open(result_path) as f:
        content = f.read()
    
    # Store in database
    cursor.execute(
        "INSERT INTO documents (filename, content) VALUES (?, ?)",
        (pdf_path, content)
    )
    
    conn.commit()
    conn.close()
```

## AWS Lambda Function

```python
import json
import boto3
from doctra import StructuredPDFParser

s3 = boto3.client('s3')
parser = StructuredPDFParser()

def lambda_handler(event, context):
    # Get PDF from S3
    bucket = event['bucket']
    key = event['key']
    
    # Download file
    local_path = f"/tmp/{key}"
    s3.download_file(bucket, key, local_path)
    
    # Parse document
    parser.parse(local_path, output_base_dir="/tmp/outputs")
    
    # Upload results back to S3
    output_dir = f"/tmp/outputs/{key.replace('.pdf', '')}"
    # ... upload logic ...
    
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete')
    }
```

## See Also

- [Basic Examples](basic-usage.md) - Getting started
- [Advanced Examples](advanced-examples.md) - Complex patterns
- [API Reference](../api/parsers.md) - API documentation

