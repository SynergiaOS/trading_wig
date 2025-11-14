# Railway Troubleshooting Decision Tree

## 🎯 Quick Problem Resolution Guide

This guide provides step-by-step troubleshooting for common Railway deployment issues. Follow the decision tree to diagnose and resolve problems quickly.

---

## 🚨 Service Deployment Issues

### Problem: Service fails to deploy

```
Service shows "Failed" status in Railway dashboard
```

**Troubleshooting Steps:**

1. **Check Build Logs**
   ```bash
   # In Railway dashboard, click on the failed deployment
   # Look for "Build Logs" tab
   ```

2. **Common Build Issues:**
   
   **A. Dockerfile not found**
   ```
   Error: Cannot find Dockerfile at path: Dockerfile.xxx
   ```
   **Solution:**
   - Verify Dockerfile exists in repository root
   - Check `railway-*.json` for correct `dockerfilePath`
   - Ensure filename matches exactly (case-sensitive)

   **B. Dependency installation failed**
   ```
   Error: npm ERR! or pip install failed
   ```
   **Solution:**
   - Check `requirements_runtime.txt` for Python services
   - Verify `package.json` for Node.js services
   - Ensure all dependencies are compatible with base image

   **C. Build context issues**
   ```
   Error: COPY failed: file not found
   ```
   **Solution:**
   - Verify files exist in repository
   - Check Dockerfile COPY paths
   - Ensure `.railwayignore` or `.gitignore` not excluding needed files

3. **Check Deploy Logs**
   ```bash
   # In Railway dashboard, click on the deployment
   # Look for "Deploy Logs" tab
   ```

4. **Common Deploy Issues:**
   
   **A. Port binding error**
   ```
   Error: Address already in use
   ```
   **Solution:**
   - Ensure service uses environment variable for port
   - Check `PORT` or `ANALYSIS_PORT` is set correctly
   - Verify no hardcoded ports in code

   **B. Missing environment variables**
   ```
   Error: KeyError or undefined variable
   ```
   **Solution:**
   - Check all required environment variables are set
   - Verify variable names match code expectations
   - Use fallback values in code

   **C. Data file not found**
   ```
   Error: File not found: wig80_current_data.json
   ```
   **Solution:**
   - Verify data file exists in repository
   - Check Dockerfile copies data files correctly
   - Ensure multiple fallback paths in code

---

## 🔌 Service Communication Issues

### Problem: Frontend cannot connect to Backend API

```
Frontend shows: "Failed to fetch" or CORS errors
```

**Troubleshooting Steps:**

1. **Verify Backend is running**
   ```bash
   curl https://backend-service.railway.app/data
   # Should return JSON data
   ```

2. **Check CORS Configuration**
   - Backend should return `Access-Control-Allow-Origin: *` header
   - Or match frontend URL if `ALLOWED_ORIGIN` is set

3. **Verify Environment Variables**
   ```bash
   # Check frontend environment variables
   VITE_API_URL=https://backend-service.railway.app
   ```
   **Solution:**
   - Update `VITE_API_URL` with correct backend URL
   - Redeploy frontend after changing variables
   - Use public URL (not `.railway.internal`) for frontend

4. **Check Network Access**
   ```bash
   # Test from local machine
   curl -H "Origin: https://frontend-service.railway.app" \
        https://backend-service.railway.app/data
   ```

5. **Common Issues:**
   
   **A. Using internal URLs in frontend**
   ```
   VITE_API_URL=http://backend.railway.internal:8000
   ```
   **Solution:**
   - Change to public URL: `https://backend-service.railway.app`
   - `.railway.internal` only works service-to-service

   **B. CORS blocked**
   ```
   Error: CORS policy: No 'Access-Control-Allow-Origin' header
   ```
   **Solution:**
   - Check backend code includes CORS headers
   - Verify `ALLOWED_ORIGIN` environment variable
   - Restart backend service

---

### Problem: Backend/Analysis cannot connect to databases

```
Error: Connection refused or timeout
```

**Troubleshooting Steps:**

1. **Verify Database Service Status**
   - Check if database service is running in Railway
   - Verify no deployment failures

2. **Check Connection URLs**
   ```bash
   # For internal network
   POCKETBASE_URL=http://pocketbase.railway.internal:8090
   
   # For public network
   POCKETBASE_URL=https://pocketbase-service.railway.app
   ```

3. **Test Connection**
   ```bash
   # From backend deploy logs, try:
   curl http://pocketbase.railway.internal:8090
   # Or from local machine if public:
   curl https://pocketbase-service.railway.app
   ```

4. **Common Issues:**
   
   **A. Service name mismatch**
   ```
   Error: Could not resolve host: pocketbase.railway.internal
   ```
   **Solution:**
   - Verify service name in Railway dashboard
   - Use exact service name in URL
   - Format: `<service-name>.railway.internal:<port>`

   **B. Port incorrect**
   ```
   Error: Connection refused
   ```
   **Solution:**
   - Check database service port configuration
   - Verify port in connection URL
   - Ensure database service exposes correct port

---

## 📊 Data & API Issues

### Problem: API returns 404 or empty data

```
curl https://backend-service.railway.app/data
# Returns: {"error": "File not found"} or empty
```

**Troubleshooting Steps:**

1. **Check Data File Existence**
   ```bash
   # Check if file exists in repository
   ls -la data/wig80_current_data.json
   ```

2. **Verify Dockerfile Copies Data**
   ```dockerfile
   # Should have line like:
   COPY data/ ./data/
   ```

3. **Check API Logs**
   ```bash
   # In Railway dashboard, check deploy logs
   # Look for: "Loading data from: /app/data/wig80_current_data.json"
   ```

4. **Test Data File**
   ```bash
   # SSH into service (if enabled) or check logs
   # Try to read the file:
   python3 -c "import json; print(json.load(open('data/wig80_current_data.json')))"
   ```

5. **Common Issues:**
   
   **A. Data file not copied**
   **Solution:**
   - Add COPY command to Dockerfile
   - Rebuild and redeploy service
   - Verify file permissions

   **B. Invalid JSON**
   ```
   Error: JSON decode error
   ```
   **Solution:**
   - Validate JSON file locally
   - Fix syntax errors
   - Recommit and redeploy

   **C. Wrong file path**
   **Solution:**
   - Check multiple fallback paths in code
   - Verify Dockerfile WORKDIR
   - Use absolute paths in code

---

### Problem: Analysis API returns errors

```
Error: Module not found or ImportError
```

**Troubleshooting Steps:**

1. **Check Import Errors**
   ```bash
   # Look in deploy logs for:
   ImportError: No module named 'telegram_alerts'
   ```

2. **Verify Requirements**
   ```bash
   # Check requirements_runtime.txt
   cat code/requirements_runtime.txt
   ```

3. **Common Issues:**
   
   **A. Missing module**
   **Solution:**
   - Add missing package to `requirements_runtime.txt`
   - Rebuild service
   - Or handle import error gracefully:
     ```python
     try:
         from telegram_alerts import PatternDetector
     except ImportError:
         PatternDetector = None
     ```

   **B. Optional dependencies**
   **Solution:**
   - Make imports optional in code
   - Provide fallback functionality
   - Log warning instead of failing

---

## 🔄 Performance & Scaling Issues

### Problem: Service is slow or times out

```
Request takes >30 seconds or returns 504 timeout
```

**Troubleshooting Steps:**

1. **Check Resource Usage**
   ```bash
   # In Railway dashboard, check Metrics tab
   # Look for: CPU > 80%, Memory > 90%
   ```

2. **Optimize Code**
   - Check for inefficient loops
   - Optimize data loading
   - Add caching if needed

3. **Increase Timeout**
   ```json
   // In railway-*.json
   {
     "deploy": {
       "healthcheckTimeout": 300
     }
   }
   ```

4. **Scale Service**
   ```bash
   # In Railway dashboard, increase resources
   # Or enable auto-scaling if available
   ```

---

## 🐛 Debugging Commands

### Useful Railway CLI Commands

```bash
# View logs
railway logs

# View environment variables
railway variables

# Set environment variable
railway variables set KEY=value

# Run command in service context
railway run bash

# Link to project
railway link

# List services
railway service
```

### Useful Curl Commands

```bash
# Test health endpoints
curl -i https://service.railway.app/
curl -i https://service.railway.app/data
curl -i https://service.railway.app/api/analysis

# Test with CORS headers
curl -H "Origin: https://frontend.railway.app" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS --verbose \
     https://backend.railway.app/data

# Test with timeout
curl -m 10 https://service.railway.app/data
```

### Check Service Status

```bash
# Check if service is running
curl -w "%{http_code}" https://service.railway.app/

# Expected: 200
# If 502: Service starting or crashed
# If 503: Service unavailable
# If 404: Wrong URL or service not deployed
```

---

## 📞 Escalation Path

If issues persist after following this guide:

1. **Check Railway Status**: https://status.railway.app
2. **Review Documentation**: https://docs.railway.app
3. **Community Support**: Railway Discord community
4. **Contact Support**: Through Railway dashboard (paid plans)

---

## 🎯 Quick Reference

| Problem | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| Build fails | Missing file | Check Dockerfile paths |
| Deploy fails | Port conflict | Use PORT env var |
| CORS error | Wrong origin | Set ALLOWED_ORIGIN=* |
| 404 error | Wrong path | Check endpoint URLs |
| Timeout | Slow code | Increase timeout or optimize |
| Can't connect DB | Wrong URL | Use .railway.internal |

---

**Last Updated**: 2025-11-08
**Version**: 1.0
**Maintained By**: DevOps Team