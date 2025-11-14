# Railway Pre-Deployment Checklist

## 🎯 Overview
This checklist ensures all prerequisites are met before deploying the Polish Finance Platform to Railway. Complete all items before proceeding with deployment.

---

## 📋 Environment Setup Verification

### 1. Railway Account & CLI
- [ ] Railway account created and verified
- [ ] Railway CLI installed (`npm i -g @railway/cli`)
- [ ] Railway CLI authenticated (`railway login`)
- [ ] Railway project created in dashboard
- [ ] GitHub repository connected to Railway

### 2. Local Environment Files
- [ ] `.railway.env` file created with Railway token
- [ ] Environment variable templates reviewed:
  - [ ] `env.railway.frontend.example`
  - [ ] `env.railway.backend.example`
  - [ ] `env.railway.analysis.example`

### 3. Docker Configuration
- [ ] All Dockerfiles exist and are valid:
  - [ ] `Dockerfile.frontend`
  - [ ] `Dockerfile.backend`
  - [ ] `Dockerfile.analysis`
- [ ] Docker builds successfully locally:
  ```bash
  docker build -f Dockerfile.frontend -t frontend-test .
  docker build -f Dockerfile.backend -t backend-test .
  docker build -f Dockerfile.analysis -t analysis-test .
  ```

---

## 🔧 Service Configuration

### 4. Railway Configuration Files
- [ ] All `railway-*.json` files exist:
  - [ ] `railway-frontend.json`
  - [ ] `railway-backend.json`
  - [ ] `railway-analysis.json`
- [ ] Configuration files validated (JSON syntax)
- [ ] Health check endpoints configured:
  - [ ] Frontend: `/`
  - [ ] Backend: `/data`
  - [ ] Analysis: `/api/analysis`

### 5. Port Configuration
- [ ] Frontend service port: `4173`
- [ ] Backend service port: `8000`
- [ ] Analysis service port: `8001`
- [ ] All services use environment variables for ports:
  - [ ] Frontend: `PORT` (fallback to 4173)
  - [ ] Backend: `PORT` (fallback to 8000)
  - [ ] Analysis: `PORT` or `ANALYSIS_PORT` (fallback to 8001)

---

## 🌐 Cross-Service Communication

### 6. Environment Variables for Service Discovery
**Frontend Service:**
- [ ] `VITE_API_URL` placeholder set
- [ ] `VITE_ANALYSIS_API_URL` placeholder set
- [ ] `VITE_REFRESH_INTERVAL=30000` configured

**Backend Service:**
- [ ] `PORT=8000` configured
- [ ] `HOST=0.0.0.0` configured
- [ ] Optional database URLs configured (if using external services)

**Analysis Service:**
- [ ] `ANALYSIS_PORT=8001` configured
- [ ] `ANALYSIS_HOST=0.0.0.0` configured
- [ ] Optional database URLs configured (if using external services)

### 7. CORS Configuration
- [ ] Backend API has CORS headers configured
- [ ] Analysis API has CORS headers configured
- [ ] `ALLOWED_ORIGIN` environment variable documented

---

## 📊 Data Files

### 8. Static Data Files
- [ ] `data/wig80_current_data.json` exists and is valid JSON
- [ ] Data file contains required structure:
  ```json
  {
    "metadata": { "collection_date": "...", "data_source": "..." },
    "companies": [...]
  }
  ```
- [ ] At least 30 companies in dataset (for WIG30 functionality)
- [ ] Each company has required fields:
  - [ ] `symbol`
  - [ ] `company_name`
  - [ ] `current_price`
  - [ ] `change_percent`
  - [ ] `trading_volume`

---

## 🔒 Security

### 9. Authentication & Access
- [ ] Railway project access permissions configured
- [ ] GitHub repository has Railway integration enabled
- [ ] No sensitive data in environment variable templates
- [ ] `.gitignore` includes `.railway.env` and sensitive files

### 10. Network Security
- [ ] Service-to-service communication plan documented
- [ ] Public vs private network usage decided
- [ ] Railway internal network hostnames documented

---

## 🧪 Pre-Deployment Testing

### 11. Local Service Testing
**Test Backend API locally:**
```bash
cd code
python3 realtime_api_server.py
# In another terminal:
curl http://localhost:8000/data
curl http://localhost:8000/wig30
```

**Test Analysis API locally:**
```bash
cd code
python3 analysis_api_server.py
# In another terminal:
curl http://localhost:8001/api/analysis
curl http://localhost:8001/api/analysis/top?limit=5
```

**Test Frontend build locally:**
```bash
cd polish-finance-platform/polish-finance-app
pnpm install
pnpm run build:prod
pnpm run preview
```

### 12. API Endpoint Validation
- [ ] Backend endpoints respond correctly:
  - [ ] `GET /data` - Returns WIG80 data
  - [ ] `GET /wig80` - Returns WIG80 data
  - [ ] `GET /wig30` - Returns top 30 companies
- [ ] Analysis endpoints respond correctly:
  - [ ] `GET /api/analysis` - Returns all analyses
  - [ ] `GET /api/analysis/top?limit=N` - Returns top N opportunities
  - [ ] `GET /api/analysis/{symbol}` - Returns specific company analysis
  - [ ] `GET /api/analysis/patterns` - Returns companies with patterns

---

## 📈 Monitoring & Logging

### 13. Health Checks
- [ ] Health check endpoints implemented in all services
- [ ] Health check paths configured in `railway-*.json` files
- [ ] Health check timeout values appropriate (100ms default)

### 14. Logging Strategy
- [ ] Services log startup information (host, port, endpoints)
- [ ] Request logging implemented
- [ ] Error logging implemented
- [ ] Log format consistent across services

---

## 🚀 Deployment Readiness

### 15. Railway Project Configuration
- [ ] Project name set appropriately
- [ ] GitHub repository connected
- [ ] Auto-deploy enabled (optional)
- [ ] Deployment region selected
- [ ] Resource limits reviewed (if applicable)

### 16. Rollback Plan
- [ ] Previous deployment version noted
- [ ] Rollback procedure documented
- [ ] Database backup plan (if applicable)
- [ ] Environment variable backup created

---

## ✅ Final Verification

### 17. Documentation Review
- [ ] All team members have access to Railway dashboard
- [ ] Deployment procedure documented
- [ ] Troubleshooting guide available
- [ ] Contact information for support documented

### 18. Stakeholder Communication
- [ ] Deployment window communicated to stakeholders
- [ ] Expected downtime communicated (if any)
- [ ] Post-deployment verification plan shared
- [ ] Rollback decision makers identified

---

## 🎯 Pre-Deployment Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Lead | | | |
| DevOps Engineer | | | |
| QA Engineer | | | |
| Product Owner | | | |

---

## 🚀 Next Steps

After completing this checklist:

1. **Run deployment testing script**: `./railway-deployment-test.sh`
2. **Deploy services** using Railway dashboard or CLI
3. **Run post-deployment verification**: `./railway-post-deploy-verify.sh`
4. **Monitor services** using Railway dashboard
5. **Verify functionality** using the testing endpoints

---

**Last Updated**: 2025-11-08
**Version**: 1.0
**Maintained By**: Development Team