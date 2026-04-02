from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import analyze, upload
import os

app = FastAPI(title="ATS Resume Checker API", version="1.0.0")

# ✅ CORS configuration - Allow all origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(upload.router, prefix="/api", tags=["upload"])

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

@app.get("/")
async def root():
    return {"message": "ATS Resume Checker API", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
