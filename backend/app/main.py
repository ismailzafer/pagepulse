from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage, pubsub_v1
import PyPDF2
import io
import os
import uuid

app = FastAPI(title="PagePulse API", description="PDF to Text Conversion Service")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Cloud clients
storage_client = storage.Client()
publisher = pubsub_v1.PublisherClient()

# Configure bucket and topic names
BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "pagepulse-storage")
TOPIC_PATH = publisher.topic_path(
    os.getenv("GCP_PROJECT_ID"), 
    os.getenv("GCP_TOPIC_NAME", "pdf-conversion")
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to PagePulse API"}

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file to Google Cloud Storage and trigger conversion process
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        blob_name = f"uploads/{file_id}/{file.filename}"
        
        # Upload to GCS
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(blob_name)
        
        # Read file content
        content = await file.read()
        
        # Verify PDF is valid
        try:
            PyPDF2.PdfReader(io.BytesIO(content))
        except:
            raise HTTPException(status_code=400, detail="Invalid PDF file")
        
        # Upload to GCS
        blob.upload_from_string(content, content_type="application/pdf")
        
        # Publish message to Pub/Sub
        message_data = {
            "file_id": file_id,
            "filename": file.filename,
            "blob_path": blob_name
        }
        publisher.publish(
            TOPIC_PATH,
            data=str(message_data).encode("utf-8")
        )
        
        return {
            "status": "success",
            "file_id": file_id,
            "message": "PDF uploaded successfully and conversion started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{file_id}")
async def get_conversion_status(file_id: str):
    """
    Check the status of a PDF conversion
    """
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        txt_blob = bucket.blob(f"conversions/{file_id}/converted.txt")
        
        if txt_blob.exists():
            return {
                "status": "completed",
                "file_id": file_id,
                "text_url": txt_blob.public_url
            }
        
        return {
            "status": "processing",
            "file_id": file_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 