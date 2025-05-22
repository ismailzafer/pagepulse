from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid
from google.cloud import storage, pubsub_v1
import os

app = FastAPI(title="PagePulse API", description="PDF to Text Conversion Service")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "pagepulse-pdf-bucket")
PUBSUB_TOPIC = os.getenv("PUBSUB_TOPIC", "pdf-conversion-topic")
GCP_PROJECT = os.getenv("GCP_PROJECT")

storage_client = storage.Client()
publisher = pubsub_v1.PublisherClient()

@app.get("/")
async def read_root():
    return {"message": "Welcome to PagePulse API"}

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file to Google Cloud Storage and trigger Cloud Function via Pub/Sub
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        pdf_filename = f"{file_id}.pdf"
        # Read file content
        content = await file.read()
        # Save PDF to GCS
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"uploads/{pdf_filename}")
        blob.upload_from_string(content, content_type="application/pdf")
        # Publish message to Pub/Sub
        topic_path = publisher.topic_path(GCP_PROJECT, PUBSUB_TOPIC)
        message = {"file_id": file_id, "filename": pdf_filename}
        publisher.publish(topic_path, data=str(message).encode("utf-8"))
        return {
            "status": "success",
            "file_id": file_id,
            "message": "PDF uploaded to Cloud Storage and conversion triggered"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{file_id}")
async def get_conversion_status(file_id: str):
    """
    Check the status of a PDF conversion in Cloud Storage
    """
    try:
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        txt_blob = bucket.blob(f"conversions/{file_id}.txt")
        if txt_blob.exists():
            return {
                "status": "completed",
                "file_id": file_id,
                "text_url": f"http://35.187.13.156/download/{file_id}"
            }
        return {
            "status": "processing",
            "file_id": file_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_id}")
async def download_text(file_id: str):
    """
    Download the converted text file from Cloud Storage
    """
    try:
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        txt_blob = bucket.blob(f"conversions/{file_id}.txt")
        if not txt_blob.exists():
            raise HTTPException(status_code=404, detail="Text file not found")
        # Download the file content to memory
        content = txt_blob.download_as_bytes()
        return FileResponse(
            io.BytesIO(content),
            media_type="text/plain",
            filename=f"converted_{file_id}.txt"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 