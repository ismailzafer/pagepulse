import base64
import json
import os
from google.cloud import storage
import PyPDF2
import io
import functions_framework

# Initialize the Google Cloud Storage client
storage_client = storage.Client()

@functions_framework.cloud_event
def convert_pdf_to_text(cloud_event):
    """
    Cloud Function triggered by Pub/Sub event to convert PDF to text
    Args:
        cloud_event: The Cloud Event that triggered this function
    """
    try:
        # Get the Pub/Sub message
        pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode()
        message_data = eval(pubsub_message)  # Convert string representation of dict to dict
        
        # Extract information from the message
        file_id = message_data["file_id"]
        blob_path = message_data["blob_path"]
        
        # Get the source bucket and blob
        bucket = storage_client.bucket(os.getenv("GCP_BUCKET_NAME", "pagepulse-storage"))
        source_blob = bucket.blob(blob_path)
        
        # Download PDF content
        pdf_content = source_blob.download_as_bytes()
        
        # Convert PDF to text
        text_content = ""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"
        
        # Upload the converted text
        output_blob_path = f"conversions/{file_id}/converted.txt"
        output_blob = bucket.blob(output_blob_path)
        output_blob.upload_from_string(text_content, content_type="text/plain")
        
        print(f"Successfully converted PDF {file_id} to text")
        return "Success", 200
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return str(e), 500 