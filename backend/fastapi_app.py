"""
FastAPI GitRot Application
Azure-optimized README generator with native HTML and AdSense integration
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
import logging
import time
import datetime
import os
import asyncio
import concurrent.futures
from contextlib import asynccontextmanager
from models.request_models import ReadmeRequest, ReadmeResponse
from models.user_model import UserAuthResponse, UserAuthRequest
from services.user_service import UserService
from database.config import get_db, create_tables
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

thread_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global thread_pool
    create_tables()
    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    logger.info("Thread pool initiated with 5 workers")
    yield
    if thread_pool:
        thread_pool.shutdown(wait=True)
        logger.info("Thread pool shutdown completed")

# Azure best practice: Initialize FastAPI with proper metadata
app = FastAPI(
    title="GitRot - AI README Generator",
    description="Azure OpenAI powered README generator for GitHub repositories",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
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

@app.post("/auth/register-or-login", response_model=UserAuthResponse)
async def register_or_login(
    auth_data: UserAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Register or login a user via OAuth
    Creates a new user if they dont exist, otherwise returns existing user
    """
    try:
        user, is_new = UserService.register_or_login(db, auth_data)

        print(f"User {user}: {is_new}")
        return UserAuthResponse(
            user_id=user.id,
            is_new=is_new,
            email=user.email,
            name=user.name,
            image = user.image
        )
    
    except ValueError as e:
        logger.warning(f"Authentication conflict: {str(e)}")
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in register_or_login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during authentication"
        )
    

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

    # Log generation attempt with client info
    client_info = get_client_info(http_request)
    log_generation_attempt(
        request.repo_url, 
        request.generation_method,
        client_info.get("user_agent")
    )
    
    try:
        logger.info(f"Generating README for repository: {sanitize_repo_name(request.repo_url)}")
        
        loop = asyncio.get_event_loop()
        readme_content = await loop.run_in_executor(
            thread_pool,
            lambda: ReadmeGeneratorApp(request).generate_readme_from_repo_url(request)
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
            reload=True,  # Set to False for production
            access_log=True
        )
    except ImportError:
        logger.error("Uvicorn not found. Please install with: pip install uvicorn[standard]")
        raise
