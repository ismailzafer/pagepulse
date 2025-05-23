# cloud-functions/pdf-converter/main.py
import os
import io
from google.cloud import storage
import PyPDF2
from flask import Request, abort, jsonify

storage_client = storage.Client()

def convert_pdf_to_text(request: Request):
    # 1) parse JSON body for event data
    request_json = request.get_json(silent=True)
    if not request_json:
        abort(400, "Expected JSON payload")

    bucket_name = request_json.get("bucket")
    pdf_blob_name = request_json.get("name")
    if not bucket_name or not pdf_blob_name:
        abort(400, "Missing 'bucket' or 'name' in JSON")

    if not pdf_blob_name.endswith(".pdf"):
        return jsonify({"status": "skipped", "reason": "not a PDF"}), 200

    # 2) now do the same processing
    bucket = storage_client.bucket(bucket_name)
    pdf_bytes = bucket.blob(pdf_blob_name).download_as_bytes()
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

    text_content = ""
    for page in reader.pages:
        text_content += page.extract_text() or ""

    file_id = os.path.splitext(os.path.basename(pdf_blob_name))[0]
    output_blob = bucket.blob(f"conversions/{file_id}.txt")
    output_blob.upload_from_string(text_content, content_type="text/plain")

    return jsonify({"status": "success", "output": f"conversions/{file_id}.txt"}), 200
