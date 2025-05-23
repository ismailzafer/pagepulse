from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
import os
import uuid
import io
import google.auth

# ─── Debug: print which service account is running ────────────────────────────────
creds, project = google.auth.default()
print(f"[DEBUG] Service account in use: {creds.service_account_email}")
# ─────────────────────────────────────────────────────────────────────────────────

from google.cloud import storage

app = FastAPI(
    title="PagePulse API",
    description="PDF to Text Conversion Service (Serverless)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "pagepulse-pdf-bucket")
storage_client = storage.Client()

@app.get("/")
async def read_root():
    return {"message": "Welcome to PagePulse API (Serverless)"}

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    # Debug: Print which service account is being used
    creds, project = google.auth.default()
    print("[DEBUG] Service account email in use:", getattr(creds, 'service_account_email', None))
    print("[DEBUG] GOOGLE_APPLICATION_CREDENTIALS:", os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    try:
        file_id = str(uuid.uuid4())
        pdf_filename = f"{file_id}.pdf"
        content = await file.read()

        # Upload PDF to GCS
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"uploads/{pdf_filename}")
        blob.upload_from_string(content, content_type="application/pdf")

        return {
            "status": "success",
            "file_id": file_id,
            "message": "PDF uploaded to Cloud Storage. Conversion will be processed by Cloud Function."
        }
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{file_id}")
async def get_conversion_status(file_id: str):
    try:
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        txt_blob = bucket.blob(f"conversions/{file_id}.txt")
        if txt_blob.exists():
            return {
                "status": "completed",
                "file_id": file_id,
                "text_url": f"/download/{file_id}"
            }
        return {
            "status": "processing",
            "file_id": file_id
        }
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_id}")
async def download_text(file_id: str):
    try:
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        txt_blob = bucket.blob(f"conversions/{file_id}.txt")
        if not txt_blob.exists():
            raise HTTPException(status_code=404, detail="Text file not found")
        content = txt_blob.download_as_bytes()
        file_like = io.BytesIO(content)
        file_like.seek(0)
        return StreamingResponse(
            file_like,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=converted_{file_id}.txt"}
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
