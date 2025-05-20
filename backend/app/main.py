from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

# Local storage paths
UPLOAD_DIR = "uploads"
CONVERSION_DIR = "conversions"

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CONVERSION_DIR, exist_ok=True)

@app.get("/")
async def read_root():
    return {"message": "Welcome to PagePulse API"}

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file and process it locally
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        pdf_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
        txt_path = os.path.join(CONVERSION_DIR, f"{file_id}.txt")
        
        # Read file content
        content = await file.read()
        
        # Verify PDF is valid
        try:
            pdf = PyPDF2.PdfReader(io.BytesIO(content))
            # Extract text from PDF
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        except:
            raise HTTPException(status_code=400, detail="Invalid PDF file")
        
        # Save PDF file
        with open(pdf_path, "wb") as f:
            f.write(content)
        
        # Save extracted text
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        return {
            "status": "success",
            "file_id": file_id,
            "message": "PDF uploaded and converted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{file_id}")
async def get_conversion_status(file_id: str):
    """
    Check the status of a PDF conversion
    """
    try:
        txt_path = os.path.join(CONVERSION_DIR, f"{file_id}.txt")
        
        if os.path.exists(txt_path):
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
    Download the converted text file
    """
    try:
        txt_path = os.path.join(CONVERSION_DIR, f"{file_id}.txt")
        
        if not os.path.exists(txt_path):
            raise HTTPException(status_code=404, detail="Text file not found")
            
        return FileResponse(
            txt_path,
            media_type="text/plain",
            filename=f"converted_{file_id}.txt"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 