# GitRot FastAPI Migration Guide

## 🚀 Successfully Migrated from Streamlit to FastAPI

GitRot has been successfully migrated from Streamlit to FastAPI for better AdSense integration and improved performance.

### ✨ What's New in FastAPI Version

#### 🎯 **Enhanced AdSense Integration**

- **Native HTML Control**: Full control over HTML head for proper AdSense script injection
- **Multiple Ad Units**: Sidebar ads with responsive design
- **AdSense Meta Tags**: Proper publisher ID configuration
- **ads.txt Support**: Automatic serving of AdSense verification file

#### 🔧 **Technical Improvements**

- **FastAPI Backend**: Modern async Python framework
- **Jinja2 Templates**: Flexible HTML templating
- **API Endpoints**: RESTful API design
- **Better Error Handling**: Comprehensive error management
- **Rate Limiting**: Built-in protection against abuse
- **Health Monitoring**: Metrics and health check endpoints

#### 🎨 **UI/UX Enhancements**

- **Responsive Design**: Bootstrap-based modern interface
- **Better Layout**: Professional sidebar with persistent ads
- **Loading States**: Smooth user experience with proper feedback
- **Download Function**: Improved README download functionality

### 📁 File Structure

```
GitRot/
├── fastapi_app.py          # Main FastAPI application
├── api_helper.py           # Utility functions and rate limiting
├── templates/
│   └── home_page.html      # Main HTML template with AdSense
├── static/
│   └── styles.css          # Additional CSS styles
├── startup_fastapi.sh      # Azure deployment startup script
├── deploy_azure.sh         # Azure deployment automation
├── web.config              # Azure App Service configuration
├── requirements.txt        # Updated dependencies
└── ads.txt                 # AdSense verification
```

### 🛠️ Key Features

#### **AdSense Monetization Ready**

- Publisher ID: `ca-pub-5478826702170077`
- Responsive ad units in sidebar
- Proper meta tag configuration
- ads.txt file for verification

#### **Azure OpenAI Integration**

- Maintained all existing README generation functionality
- Two generation methods: Standard and with Examples
- Proper error handling and logging
- Azure best practices implementation

#### **Performance & Monitoring**

- Request metrics tracking
- Health check endpoints
- Rate limiting (50 requests/hour per IP)
- Structured logging for Azure monitoring

### 🚀 Running the Application

#### **Local Development**

```bash
# Activate virtual environment
source gitrot/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI application
python fastapi_app.py
```

#### **Access Points**

- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

### ☁️ Azure Deployment

#### **Automated Deployment**

```bash
# Run the deployment script
./deploy_azure.sh
```

#### **Manual Deployment Steps**

1. **Create Azure Resources**:

   ```bash
   az group create --name gitrot-rg --location eastus
   az appservice plan create --name gitrot-plan --resource-group gitrot-rg --sku F1 --is-linux
   az webapp create --name gitrot-fastapi --resource-group gitrot-rg --plan gitrot-plan --runtime "PYTHON|3.9"
   ```

2. **Configure Settings**:

   ```bash
   az webapp config set --name gitrot-fastapi --resource-group gitrot-rg --startup-file "startup_fastapi.sh"
   ```

3. **Deploy Code**:
   ```bash
   az webapp deploy --name gitrot-fastapi --resource-group gitrot-rg --src-path .
   ```

### 🌐 Custom Domain Configuration

#### **DNS Setup**

1. Add CNAME record: `gitrot.mcaupybugs.com` → `gitrot-fastapi.azurewebsites.net`
2. Configure in Azure:
   ```bash
   az webapp config hostname add --webapp-name gitrot-fastapi --resource-group gitrot-rg --hostname gitrot.mcaupybugs.com
   ```

### 📊 API Endpoints

#### **Main Endpoints**

- `GET /` - Main application interface
- `POST /api/generate-readme` - Generate README from repository
- `GET /health` - Health check with metrics
- `GET /metrics` - Application metrics
- `GET /ads.txt` - AdSense verification file

#### **API Usage Example**

```javascript
const response = await fetch("/api/generate-readme", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    repo_url: "https://github.com/user/repo",
    generation_method: "Standard README",
  }),
});
const result = await response.json();
```

### 🔒 Security Features

- **Rate Limiting**: 50 requests per hour per IP
- **Input Validation**: GitHub URL format validation
- **Error Handling**: Comprehensive error responses
- **HTTPS Redirect**: Configured for production
- **Security Headers**: Implemented via Azure configuration

### 📈 Monitoring & Analytics

#### **Built-in Metrics**

- Total requests processed
- Error rates and counts
- Average response times
- README generation statistics
- Application uptime

#### **Azure Monitoring**

- Application Insights integration ready
- Structured logging for analysis
- Health check endpoints for monitoring
- Performance metrics collection

### 🎯 AdSense Optimization

#### **Implementation Details**

- **Script Placement**: Proper head section injection
- **Ad Units**: Responsive sidebar placements
- **Meta Tags**: Publisher ID configuration
- **Verification**: ads.txt file serving
- **JavaScript Integration**: Native AdSense API usage

#### **Ad Unit Configuration**

```html
<ins
  class="adsbygoogle"
  style="display:block"
  data-ad-client="ca-pub-5478826702170077"
  data-ad-slot="1234567890"
  data-ad-format="auto"
  data-full-width-responsive="true"
></ins>
```

### 🔄 Migration Benefits

#### **From Streamlit Limitations**

- ✅ **Full HTML Control**: No more iframe restrictions
- ✅ **Proper AdSense Integration**: Native script injection
- ✅ **Better Performance**: Async FastAPI framework
- ✅ **API Flexibility**: RESTful endpoint design
- ✅ **Professional UI**: Custom styling and layout

#### **Maintained Features**

- ✅ **Azure OpenAI Integration**: All existing functionality
- ✅ **Repository Processing**: Same cloning and analysis
- ✅ **README Generation**: Both standard and example modes
- ✅ **Download Capability**: Improved file download
- ✅ **Error Handling**: Enhanced error management

### 🚨 Important Notes

#### **Environment Variables**

Ensure these environment variables are set in Azure:

- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION`

#### **Dependencies**

The application requires:

- Python 3.9+
- FastAPI and Uvicorn
- All existing GitRot dependencies
- Git executable in system PATH

#### **AdSense Approval**

- Replace placeholder ad slots with actual AdSense units
- Ensure site meets AdSense quality guidelines
- Configure proper ad placements for optimal revenue

### 🎉 Success Metrics

The migration delivers:

- **100% AdSense Compatibility**: Full script control
- **Modern Architecture**: FastAPI + Jinja2 templates
- **Better Performance**: Async request handling
- **Professional Interface**: Bootstrap-based design
- **Enhanced Monitoring**: Built-in metrics and health checks
- **Azure Optimized**: Following Azure best practices

### 📞 Support

For deployment issues or questions:

1. Check Azure App Service logs
2. Review health check endpoint
3. Monitor metrics for performance
4. Verify AdSense configuration

---

**🎯 GitRot FastAPI - Ready for Production with Full AdSense Integration!**
