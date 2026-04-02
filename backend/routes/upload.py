from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
from datetime import datetime
import re

router = APIRouter()

@router.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse resume file"""
    try:
        print(f"📄 Received file: {file.filename}")
        
        # Check file type
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are allowed"
            )
        
        # Read file content
        content = await file.read()
        print(f"📏 File size: {len(content)} bytes")
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Extract text based on file type
        extracted_text = await extract_text_from_file(content, file.filename)
        
        print(f"📝 Extracted text length: {len(extracted_text)} characters")
        
        if not extracted_text or len(extracted_text) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract enough text from file. Please paste text manually."
            )
        
        return {
            "success": True,
            "filename": file.filename,
            "extracted_text": extracted_text,
            "file_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

async def extract_text_from_file(content: bytes, filename: str) -> str:
    """Extract text from PDF or DOCX file"""
    
    if filename.lower().endswith('.pdf'):
        return await extract_pdf_text(content)
    elif filename.lower().endswith('.docx'):
        return await extract_docx_text(content)
    else:
        return ""

async def extract_pdf_text(content: bytes) -> str:
    """Extract text from PDF"""
    try:
        # Try PyPDF2 first
        import PyPDF2
        import io
        
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        if text.strip():
            return clean_text(text)
        
        # If PyPDF2 fails, try pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return clean_text(text)
        except ImportError:
            pass
        
        return text.strip()
        
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

async def extract_docx_text(content: bytes) -> str:
    """Extract text from DOCX"""
    try:
        from docx import Document
        import io
        
        doc = Document(io.BytesIO(content))
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        
        return clean_text(text)
        
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return ""

def clean_text(text: str) -> str:
    """Clean extracted text"""
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[^\w\s\.\,\-\#\+\(\)\/\@\:]', '', text)
    return text.strip()