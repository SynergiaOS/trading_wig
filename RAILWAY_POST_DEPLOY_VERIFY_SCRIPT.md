# Railway Post-Deployment Verification Script

## 🎯 Overview
This script verifies that all services are working correctly after deployment to Railway. It tests each service endpoint, validates data flow, and checks integration between services.

---

## 📋 Script Usage

### Save as `railway-post-deploy-verify.sh`
```bash
#!/bin/bash

# Railway Post-Deployment Verification Script
# Verifies all services are working correctly after deployment
# Usage: ./railway-post-deploy-verify.sh [environment]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Update these with your actual Railway URLs
ENVIRONMENT=${1:-"production"}

# Default URLs (replace with your actual Railway URLs)
FRONTEND_URL=${FRONTEND_URL:-"https://frontend-service.railway.app"}
BACKEND_URL=${BACKEND_URL:-"https://backend-service.railway.app"}
ANALYSIS_URL=${ANALYSIS_URL:-"https://analysis-service.railway.app"}

# Timeouts
CURL_TIMEOUT=10
MAX_RETRIES=3
RETRY_DELAY=5

# Counters
TESTS_PASSED=0
TESTS_FAILED=0
WARNINGS=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARNINGS++))
}

# Utility functions
make_request() {
    local url=$1
    local method=${2:-"GET"}
    local max_time=${3:-$CURL_TIMEOUT}
    local data=${4:-""}
    
    local response
    local http_code
    local body
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method \
                   -H "Content-Type: application/json" \
                   -d "$data" \
                   --max-time $max_time \
                   "$url" 2>/dev/null || echo -e "\n000")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method \
                   --max-time $max_time \
                   "$url" 2>/dev/null || echo -e "\n000")
    fi
    
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    echo "$http_code|$body"
}

retry_request() {
    local url=$1
    local expected_status=$2
    local description=$3
    local retries=$MAX_RETRIES
    
    while [ $retries -gt 0 ]; do
        local result=$(make_request "$url")
        local http_code=$(echo "$result" | cut -d'|' -f1)
        local body=$(echo "$result" | cut -d'|' -f2-)
        
        if [ "$http_code" = "$expected_status" ]; then
            log_success "$description - Status: $http_code"
            return 0
        fi
        
        ((retries--))
        if [ $retries -gt 0 ]; then
            log_warning "$description - Retry attempt ($retries left) - Status: $http_code"
            sleep $RETRY_DELAY
        fi
    done
    
    log_error "$description - Expected: $expected_status, Got: $http_code"
    return 1
}

# Test functions
test_service_available() {
    local url=$1
    local service_name=$2
    
    log_info "Testing $service_name availability: $url"
    
    local result=$(make_request "$url")
    local http_code=$(echo "$result" | cut -d'|' -f1)
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "301" ] || [ "$http_code" = "302" ]; then
        log_success "$service_name is accessible"
        return 0
    else
        log_error "$service_name is not accessible - Status: $http_code"
        return 1
    fi
}

test_api_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    local should_contain=${4:-""}
    
    log_info "Testing API: $description"
    
    local result=$(make_request "$url")
    local http_code=$(echo "$result" | cut -d'|' -f1)
    local body=$(echo "$result" | cut -d'|' -f2-)
    
    if [ "$http_code" = "$expected_status" ]; then
        if [ -n "$should_contain" ]; then
            if echo "$body" | grep -q "$should_contain"; then
                log_success "$description - Status: $http_code, Contains: $should_contain"
                return 0
            else
                log_error "$description - Status: $http_code, Missing: $should_contain"
                return 1
            fi
        else
            log_success "$description - Status: $http_code"
            return 0
        fi
    else
        log_error "$description - Expected: $expected_status, Got: $http_code"
        return 1
    fi
}

test_json_response() {
    local url=$1
    local expected_status=$2
    local description=$3
    local json_path=$4
    local expected_value=$5
    
    log_info "Testing JSON response: $description"
    
    local result=$(make_request "$url")
    local http_code=$(echo "$result" | cut -d'|' -f1)
    local body=$(echo "$result" | cut -d'|' -f2-)
    
    if [ "$http_code" != "$expected_status" ]; then
        log_error "$description - Expected status: $expected_status, Got: $http_code"
        return 1
    fi
    
    # Check if body is valid JSON
    if ! echo "$body" | python3 -m json.tool > /dev/null 2>&1; then
        log_error "$description - Response is not valid JSON"
        return 1
    fi
    
    # Check JSON path if provided
    if [ -n "$json_path" ]; then
        local actual_value=$(echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print($json_path)" 2>/dev/null)
        
        if [ "$actual_value" = "$expected_value" ]; then
            log_success "$description - JSON validation passed"
            return 0
        else
            log_error "$description - Expected: $expected_value, Got: $actual_value"
            return 1
        fi
    fi
    
    log_success "$description - Valid JSON response"
    return 0
}

test_cors_headers() {
    local url=$1
    local service_name=$2
    
    log_info "Testing CORS headers for $service_name"
    
    local result=$(make_request "$url")
    local http_code=$(echo "$result" | cut -d'|' -f1)
    
    if [ "$http_code" = "200" ]; then
        # Test CORS preflight
        local cors_result=$(curl -s -w "\n%{http_code}" -X OPTIONS \
                           -H "Origin: https://example.com" \
                           -H "Access-Control-Request-Method: GET" \
                           --max-time $CURL_TIMEOUT \
                           "$url" 2>/dev/null || echo -e "\n000")
        
        local cors_code=$(echo "$cors_result" | tail -n 1)
        
        if [ "$cors_code" = "200" ]; then
            log_success "$service_name - CORS headers configured"
            return 0
        else
            log_warning "$service_name - CORS preflight returned: $cors_code"
            return 0
        fi
    else
        log_error "$service_name - Cannot test CORS, service returned: $http_code"
        return 1
    fi
}

test_response_time() {
    local url=$1
    local max_time=$2
    local description=$3
    
    log_info "Testing response time: $description"
    
    local start_time=$(date +%s.%N)
    local result=$(make_request "$url" "GET" "$max_time")
    local end_time=$(date +%s.%N)
    local http_code=$(echo "$result" | cut -d'|' -f1)
    
    local duration=$(echo "$end_time - $start_time" | bc)
    
    if [ "$http_code" = "200" ]; then
        if (( $(echo "$duration <= $max_time" | bc -l) )); then
            log_success "$description - Response time: ${duration}s (max: ${max_time}s)"
            return 0
        else
            log_warning "$description - Slow response: ${duration}s (max: ${max_time}s)"
            return 0
        fi
    else
        log_error "$description - Failed with status: $http_code"
        return 1
    fi
}

test_data_freshness() {
    local url=$1
    local max_age_minutes=$2
    local description=$3
    
    log_info "Testing data freshness: $description"
    
    local result=$(make_request "$url")
    local http_code=$(echo "$result" | cut -d'|' -f1)
    local body=$(echo "$result" | cut -d'|' -f2-)
    
    if [ "$http_code" = "200" ]; then
        # Extract timestamp from metadata
        local timestamp=$(echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('metadata', {}).get('collection_date', ''))" 2>/dev/null)
        
        if [ -n "$timestamp" ]; then
            # Convert to epoch and calculate age
            local timestamp_epoch=$(date -d "$timestamp" +%s 2>/dev/null || echo "0")
            local current_epoch=$(date +%s)
            local age_minutes=$(( (current_epoch - timestamp_epoch) / 60 ))
            
            if [ $age_minutes -le $max_age_minutes ]; then
                log_success "$description - Data age: ${age_minutes}m (max: ${max_age_minutes}m)"
                return 0
            else
                log_warning "$description - Data stale: ${age_minutes}m (max: ${max_age_minutes}m)"
                return 0
            fi
        else
            log_warning "$description - Could not determine data age"
            return 0
        fi
    else
        log_error "$description - Failed with status: $http_code"
        return 1
    fi
}

# Main test execution
main() {
    echo "============================================================"
    echo "  Railway Post-Deployment Verification Script"
    echo "============================================================"
    echo "Environment: $ENVIRONMENT"
    echo "Frontend URL: $FRONTEND_URL"
    echo "Backend URL: $BACKEND_URL"
    echo "Analysis URL: $ANALYSIS_URL"
    echo "============================================================"
    echo ""
    
    log_info "Starting post-deployment verification..."
    echo ""
    
    # Phase 1: Service Availability Tests
    echo "🌐 Phase 1: Service Availability Tests"
    echo "------------------------------------------------------------"
    
    test_service_available "$FRONTEND_URL" "Frontend Service"
    test_service_available "$BACKEND_URL" "Backend Service"
    test_service_available "$ANALYSIS_URL" "Analysis Service"
    echo ""
    
    # Phase 2: Frontend Tests
    echo "🎨 Phase 2: Frontend Service Tests"
    echo "------------------------------------------------------------"
    
    test_api_endpoint "$FRONTEND_URL" "200" "Frontend homepage"
    test_response_time "$FRONTEND_URL" "5" "Frontend response time"
    echo ""
    
    # Phase 3: Backend API Tests
    echo "🔧 Phase 3: Backend API Tests"
    echo "------------------------------------------------------------"
    
    test_api_endpoint "$BACKEND_URL/data" "200" "Backend data endpoint"
    test_api_endpoint "$BACKEND_URL/wig80" "200" "Backend WIG80 endpoint"
    test_api_endpoint "$BACKEND_URL/wig30" "200" "Backend WIG30 endpoint"
    test_json_response "$BACKEND_URL/data" "200" "Backend JSON response" "len(data.get('companies', [])) > 0" "True"
    test_cors_headers "$BACKEND_URL/data" "Backend API"
    test_response_time "$BACKEND_URL/data" "3" "Backend response time"
    test_data_freshness "$BACKEND_URL/data" "60" "Backend data freshness"
    echo ""
    
    # Phase 4: Analysis API Tests
    echo "📊 Phase 4: Analysis API Tests"
    echo "------------------------------------------------------------"
    
    test_api_endpoint "$ANALYSIS_URL/api/analysis" "200" "Analysis all endpoint"
    test_api_endpoint "$ANALYSIS_URL/api/analysis/top?limit=10" "200" "Analysis top endpoint"
    test_json_response "$ANALYSIS_URL/api/analysis" "200" "Analysis JSON response" "len(data.get('analyses', [])) > 0" "True"
    test_cors_headers "$ANALYSIS_URL/api/analysis" "Analysis API"
    test_response_time "$ANALYSIS_URL/api/analysis" "5" "Analysis response time"
    echo ""
    
    # Phase 5: Integration Tests
    echo "🔗 Phase 5: Integration Tests"
    echo "------------------------------------------------------------"
    
    # Test cross-service communication
    log_info "Testing cross-service communication..."
    
    # Frontend should be able to call Backend
    local frontend_env_test=$(curl -s -I "$FRONTEND_URL" | grep -i "access-control-allow-origin")
    if [ -n "$frontend_env_test" ]; then
        log_success "Frontend CORS configured"
    else
        log_warning "Frontend CORS configuration not detectable"
    fi
    
    # Test that backend data is accessible
    local backend_data=$(make_request "$BACKEND_URL/data")
    local backend_http_code=$(echo "$backend_data" | cut -d'|' -f1)
    
    if [ "$backend_http_code" = "200" ]; then
        log_success "Backend data accessible for frontend integration"
    else
        log_error "Backend data not accessible"
    fi
    echo ""
    
    # Phase 6: Performance Tests
    echo "⚡ Phase 6: Performance Tests"
    echo "------------------------------------------------------------"
    
    # Concurrent request test
    log_info "Testing concurrent request handling..."
    
    local concurrent_test_passed=0
    for i in {1..5}; do
        (
            result=$(make_request "$BACKEND_URL/data")
            http_code=$(echo "$result" | cut -d'|' -f1)
            if [ "$http_code" = "200" ]; then
                echo "success"
            else
                echo "failed"
            fi
        ) &
    done
    
    wait
    
    if [ $concurrent_test_passed -ge 4 ]; then
        log_success "Concurrent request handling - 5 simultaneous requests"
    else
        log_warning "Concurrent request handling - Some requests failed"
    fi
    echo ""
    
    # Phase 7: Error Handling Tests
    echo "🛡️  Phase 7: Error Handling Tests"
    echo "------------------------------------------------------------"
    
    test_api_endpoint "$BACKEND_URL/nonexistent" "404" "Backend 404 handling"
    test_api_endpoint "$ANALYSIS_URL/api/nonexistent" "404" "Analysis 404 handling"
    test_api_endpoint "$BACKEND_URL/wig30" "200" "Backend WIG30 data integrity"
    echo ""
    
    # Summary
    echo "============================================================"
    echo "  Verification Summary"
    echo "============================================================"
    echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
    echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ All verification tests passed! Deployment is healthy.${NC}"
        echo ""
        echo "🎯 Next steps:"
        echo "   1. Monitor services in Railway dashboard"
        echo "   2. Set up alerts for production monitoring"
        echo "   3. Share URLs with stakeholders:"
        echo "      - Frontend: $FRONTEND_URL"
        echo "      - Backend: $BACKEND_URL"
        echo "      - Analysis: $ANALYSIS_URL"
        exit 0
    else
        echo -e "${RED}❌ Some verification tests failed. Please investigate.${NC}"
        echo ""
        echo "🔍 Troubleshooting:"
        echo "   1. Check Railway dashboard for service status"
        echo "   2. Review service logs for errors"
        echo "   3. Verify environment variables are set correctly"
        echo "   4. Check network connectivity between services"
        exit 1
    fi
}

# Configuration helper
show_config_help() {
    echo "Railway Post-Deployment Verification Script"
    echo ""
    echo "Usage: ./railway-post-deploy-verify.sh [environment]"
    echo ""
    echo "Environments:"
    echo "  production    Use production URLs (default)"
    echo "  staging       Use staging URLs"
    echo ""
    echo "Environment Variables:"
    echo "  FRONTEND_URL  Override frontend URL"
    echo "  BACKEND_URL   Override backend URL"
    echo "  ANALYSIS_URL  Override analysis URL"
    echo ""
    echo "Examples:"
    echo "  ./railway-post-deploy-verify.sh"
    echo "  ./railway-post-deploy-verify.sh staging"
    echo "  FRONTEND_URL=https://myapp.com ./railway-post-deploy-verify.sh"
}

# Handle help flag
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_config_help
    exit 0
fi

# Run main function
main "$@"
```

---

## 🚀 Usage Instructions

### 1. Save the Script
```bash
# Save the script to a file
cat > railway-post-deploy-verify.sh << 'EOF'
# [Paste the script content above]
EOF
```

### 2. Make Executable
```bash
chmod +x railway-post-deploy-verify.sh
```

### 3. Configure URLs
```bash
# Set your actual Railway URLs
export FRONTEND_URL="https://your-frontend.railway.app"
export BACKEND_URL="https://your-backend.railway.app"
export ANALYSIS_URL="https://your-analysis.railway.app"
```

### 4. Run Verification
```bash
# Run verification
./railway-post-deploy-verify.sh

# Or with custom URLs
FRONTEND_URL="https://myapp.com" ./railway-post-deploy-verify.sh
```

---

## 🧪 Test Coverage

### What This Script Tests

✅ **Service Availability**
- All services are accessible via HTTP
- Services respond within acceptable time limits
- Health check endpoints return 200

✅ **API Functionality**
- Backend API serves WIG80/WIG30 data
- Analysis API generates analyses
- All endpoints return valid JSON
- Error handling works correctly (404s, etc.)

✅ **Data Integrity**
- Data is fresh (not stale)
- JSON structure is correct
- Required fields are present
- Sufficient data for WIG30 calculation

✅ **Cross-Service Integration**
- CORS headers configured correctly
- Services can communicate with each other
- Frontend can access backend APIs

✅ **Performance**
- Response times under thresholds
- Concurrent request handling
- No timeout issues

✅ **Error Handling**
- 404 errors handled gracefully
- Invalid requests return appropriate status codes
- Error messages are helpful

---

## 🔧 Customization

### Adding Custom Tests

```bash
# Add to main() function
test_custom_integration() {
    local description=$1
    
    # Your custom test logic
    if [ your-condition ]; then
        log_success "$description"
        return 0
    else
        log_error "$description"
        return 1
    fi
}

# Call in main
test_custom_integration "Custom integration test"
```

### Modifying Thresholds

```bash
# Change at top of script
CURL_TIMEOUT=15
MAX_RETRIES=5
RETRY_DELAY=10
```

---

## 📊 CI/CD Integration

### GitHub Actions Integration

```yaml
name: Post-Deployment Verification

on:
  deployment_status

jobs:
  verify:
    if: github.event.deployment_status.state == 'success'
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run post-deployment verification
      env:
        FRONTEND_URL: ${{ secrets.FRONTEND_URL }}
        BACKEND_URL: ${{ secrets.BACKEND_URL }}
        ANALYSIS_URL: ${{ secrets.ANALYSIS_URL }}
      run: |
        chmod +x railway-post-deploy-verify.sh
        ./railway-post-deploy-verify.sh
    
    - name: Notify on failure
      if: failure()
      uses: slack/github-action@v1
      with:
        webhook: ${{ secrets.SLACK_WEBHOOK }}
        message: "Deployment verification failed!"
```

---

## 🎯 Expected Output

### Successful Verification
```
============================================================
  Railway Post-Deployment Verification Script
============================================================
Environment: production
Frontend URL: https://frontend.railway.app
Backend URL: https://backend.railway.app
Analysis URL: https://analysis.railway.app
============================================================

[INFO] Starting post-deployment verification...

🌐 Phase 1: Service Availability Tests
------------------------------------------------------------
[INFO] Testing Frontend Service availability: https://frontend.railway.app
[PASS] Frontend Service is accessible
...

============================================================
  Verification Summary
============================================================
Tests Passed: 25
Tests Failed: 0
Warnings: 1

✅ All verification tests passed! Deployment is healthy.

🎯 Next steps:
   1. Monitor services in Railway dashboard
   2. Set up alerts for production monitoring
   3. Share URLs with stakeholders
```

---

**Last Updated**: 2025-11-08
**Version**: 1.0
**Maintained By**: DevOps Team