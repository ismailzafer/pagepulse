import os
from google.cloud import storage
import PyPDF2
import io
import functions_framework

storage_client = storage.Client()

@functions_framework.http
def convert_pdf_to_text(request):
    if request.method != 'POST':
        return 'Method Not Allowed', 405

    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    try:
        # PDF dosyasını oku
        pdf_bytes = file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"

        # Sonucu GCS'ye kaydet (opsiyonel)
        bucket_name = os.getenv("BUCKET_NAME", "pagepulse-pdf-bucket")
        output_blob_path = f"conversions/{file.filename}.txt"
        bucket = storage_client.bucket(bucket_name)
        output_blob = bucket.blob(output_blob_path)
        output_blob.upload_from_string(text_content, content_type="text/plain")

        return f"PDF converted and saved as {output_blob_path}", 200

    except Exception as e:
        return f"Error processing PDF: {str(e)}", 500