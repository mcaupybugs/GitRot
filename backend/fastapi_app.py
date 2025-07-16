"""
FastAPI GitRot Application
Azure-optimized README generator with native HTML and AdSense integration
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import logging
import datetime
import os
from app import ReadmeGeneratorApp
from api_helper import (
    log_request_metrics, 
    validate_github_url, 
    sanitize_repo_name,
    format_error_response,
    log_generation_attempt,
    get_client_info,
    check_rate_limit,
    metrics
)

# Azure best practice: Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Azure best practice: Initialize FastAPI with proper metadata
app = FastAPI(
    title="GitRot - AI README Generator",
    description="Azure OpenAI powered README generator for GitHub repositories",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        "https://gitrot.vercel.app",  # Add your production domain when deployed
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Pydantic models for API requests
class ReadmeRequest(BaseModel):
    repo_url: str
    generation_method: str = "Standard README"

class ReadmeResponse(BaseModel):
    success: bool
    readme_content: str = ""
    error_message: str = ""
    generation_timestamp: str
    repo_url: str
    generation_method: str

# Azure best practice: Initialize core services with error handling
try:
    readme_app = ReadmeGeneratorApp()
    logger.info("GitRot application initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize GitRot application: {str(e)}")
    readme_app = None

@app.get("/", response_class=HTMLResponse)
@log_request_metrics
async def home_page(request: Request):
    """
    Serve the main GitRot HTML page with full AdSense integration
    Azure best practice: Use proper error handling and logging
    """
    try:
        return templates.TemplateResponse(
            "home_page.html", 
            {
                "request": request,
                "adsense_publisher_id": "ca-pub-5478826702170077",
                "app_version": "2.0.0",
                "current_year": datetime.datetime.now().year
            }
        )
    except Exception as e:
        logger.error(f"Error serving home page: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/generate-readme", response_model=ReadmeResponse)
@log_request_metrics
async def generate_readme(request: ReadmeRequest, http_request: Request):
    """
    Generate README using Azure OpenAI
    Azure best practice: Implement proper error handling and retry logic
    """
    # Rate limiting check
    if not check_rate_limit(http_request):
        raise HTTPException(
            status_code=429, 
            detail="Too many requests. Please try again later."
        )
    
    # Input validation
    if not validate_github_url(request.repo_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub repository URL format"
        )
    
    if not readme_app:
        raise HTTPException(
            status_code=503, 
            detail="README generator service is unavailable"
        )
    
    # Log generation attempt with client info
    client_info = get_client_info(http_request)
    log_generation_attempt(
        request.repo_url, 
        request.generation_method,
        client_info.get("user_agent")
    )
    
    try:
        logger.info(f"Generating README for repository: {sanitize_repo_name(request.repo_url)}")
        
        # Generate README using existing logic
        readme_content = readme_app.generate_readme_from_repo_url(
            request.repo_url, 
            request.generation_method
        )
        
        response = ReadmeResponse(
            success=True,
            readme_content=readme_content,
            generation_timestamp=datetime.datetime.now().isoformat(),
            repo_url=request.repo_url,
            generation_method=request.generation_method
        )
        
        logger.info(f"Successfully generated README for {sanitize_repo_name(request.repo_url)}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating README: {str(e)}")
        return ReadmeResponse(
            success=False,
            error_message=str(e),
            generation_timestamp=datetime.datetime.now().isoformat(),
            repo_url=request.repo_url,
            generation_method=request.generation_method
        )

@app.get("/health")
@log_request_metrics
async def health_check():
    """Azure best practice: Implement health check endpoint"""
    app_metrics = metrics.get_metrics()
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "GitRot FastAPI",
        "version": "2.0.0",
        "metrics": app_metrics
    }

@app.get("/metrics")
@log_request_metrics
async def get_metrics():
    """Azure best practice: Expose application metrics"""
    return metrics.get_metrics()

@app.get("/ads.txt")
async def ads_txt():
    """Serve ads.txt for Google AdSense verification"""
    try:
        with open("ads.txt", "r") as f:
            content = f.read()
        return HTMLResponse(content=content, media_type="text/plain")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="ads.txt not found")

# Azure best practice: Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    # Azure best practice: Configure for production deployment
    try:
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(
            "fastapi_app:app",
            host="0.0.0.0",
            port=port,
            reload=False,  # Set to False for production
            access_log=True
        )
    except ImportError:
        logger.error("Uvicorn not found. Please install with: pip install uvicorn[standard]")
        raise
