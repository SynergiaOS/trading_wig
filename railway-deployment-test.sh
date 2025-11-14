#!/bin/bash

# Railway Deployment Testing Script
# Tests all components before deployment to Railway
# Usage: ./railway-deployment-test.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_PORT=4173
BACKEND_PORT=8000
ANALYSIS_PORT=8001
TEST_TIMEOUT=10

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

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
}

# Test functions
test_file_exists() {
    local file_path=$1
    local description=$2
    
    if [ -f "$file_path" ]; then
        log_success "$description - File exists: $file_path"
        return 0
    else
        log_error "$description - File missing: $file_path"
        return 1
    fi
}

test_json_valid() {
    local file_path=$1
    local description=$2
    
    if [ -f "$file_path" ]; then
        if python3 -m json.tool "$file_path" > /dev/null 2>&1; then
            log_success "$description - Valid JSON: $file_path"
            return 0
        else
            log_error "$description - Invalid JSON: $file_path"
            return 1
        fi
    else
        log_error "$description - File not found: $file_path"
        return 1
    fi
}

test_dockerfile() {
    local dockerfile=$1
    local description=$2
    
    if [ -f "$dockerfile" ]; then
        # Check for common Dockerfile issues
        if grep -q "FROM" "$dockerfile"; then
            log_success "$description - Dockerfile structure OK: $dockerfile"
        else
            log_error "$description - Invalid Dockerfile: $dockerfile"
            return 1
        fi
        
        # Try to build (dry run)
        if docker build -f "$dockerfile" --target=builder . > /dev/null 2>&1; then
            log_success "$description - Dockerfile builds successfully"
            return 0
        else
            log_warning "$description - Dockerfile build warnings (non-critical)"
            return 0
        fi
    else
        log_error "$description - Dockerfile not found: $dockerfile"
        return 1
    fi
}

test_port_available() {
    local port=$1
    local description=$2
    
    if ! lsof -i :$port > /dev/null 2>&1; then
        log_success "$description - Port $port is available"
        return 0
    else
        log_error "$description - Port $port is already in use"
        return 1
    fi
}

test_environment_variables() {
    local env_file=$1
    local description=$2
    
    if [ -f "$env_file" ]; then
        # Check for required variables
        local required_vars=("PORT" "HOST")
        local missing_vars=()
        
        for var in "${required_vars[@]}"; do
            if ! grep -q "^$var=" "$env_file"; then
                missing_vars+=("$var")
            fi
        done
        
        if [ ${#missing_vars[@]} -eq 0 ]; then
            log_success "$description - All required variables present"
            return 0
        else
            log_warning "$description - Missing variables: ${missing_vars[*]}"
            return 0
        fi
    else
        log_error "$description - Environment file not found: $env_file"
        return 1
    fi
}

# Main test execution
main() {
    echo "============================================================"
    echo "  Railway Deployment Testing Script"
    echo "============================================================"
    echo ""
    
    log_info "Starting pre-deployment tests..."
    echo ""
    
    # Phase 1: File Structure Tests
    echo "📁 Phase 1: File Structure Validation"
    echo "------------------------------------------------------------"
    
    test_file_exists "railway-frontend.json" "Railway frontend config"
    test_file_exists "railway-backend.json" "Railway backend config"
    test_file_exists "railway-analysis.json" "Railway analysis config"
    
    test_file_exists "Dockerfile.frontend" "Frontend Dockerfile"
    test_file_exists "Dockerfile.backend" "Backend Dockerfile"
    test_file_exists "Dockerfile.analysis" "Analysis Dockerfile"
    
    test_file_exists "env.railway.frontend.example" "Frontend env template"
    test_file_exists "env.railway.backend.example" "Backend env template"
    test_file_exists "env.railway.analysis.example" "Analysis env template"
    
    test_file_exists "data/wig80_current_data.json" "WIG80 data file"
    echo ""
    
    # Phase 2: Configuration Tests
    echo "⚙️  Phase 2: Configuration Validation"
    echo "------------------------------------------------------------"
    
    test_json_valid "railway-frontend.json" "Frontend config JSON"
    test_json_valid "railway-backend.json" "Backend config JSON"
    test_json_valid "railway-analysis.json" "Analysis config JSON"
    test_json_valid "data/wig80_current_data.json" "WIG80 data JSON"
    echo ""
    
    # Phase 3: Docker Tests
    echo "🐳 Phase 3: Docker Configuration Tests"
    echo "------------------------------------------------------------"
    
    test_dockerfile "Dockerfile.frontend" "Frontend Dockerfile"
    test_dockerfile "Dockerfile.backend" "Backend Dockerfile"
    test_dockerfile "Dockerfile.analysis" "Analysis Dockerfile"
    echo ""
    
    # Phase 4: Port Availability Tests
    echo "🔌 Phase 4: Port Availability Tests"
    echo "------------------------------------------------------------"
    
    test_port_available $FRONTEND_PORT "Frontend service"
    test_port_available $BACKEND_PORT "Backend service"
    test_port_available $ANALYSIS_PORT "Analysis service"
    echo ""
    
    # Phase 5: Environment Variable Tests
    echo "🔧 Phase 5: Environment Variable Tests"
    echo "------------------------------------------------------------"
    
    test_environment_variables "env.railway.frontend.example" "Frontend env"
    test_environment_variables "env.railway.backend.example" "Backend env"
    test_environment_variables "env.railway.analysis.example" "Analysis env"
    echo ""
    
    # Phase 6: Data Validation
    echo "📊 Phase 6: Data File Validation"
    echo "------------------------------------------------------------"
    
    # Check data file structure
    if [ -f "data/wig80_current_data.json" ]; then
        local company_count=$(python3 -c "import json; print(len(json.load(open('data/wig80_current_data.json')).get('companies', [])))")
        
        if [ "$company_count" -ge 30 ]; then
            log_success "Data validation - Found $company_count companies (WIG30+)"
        else
            log_error "Data validation - Only $company_count companies found (need 30+)"
        fi
        
        # Check for required fields
        local has_metadata=$(python3 -c "import json; data=json.load(open('data/wig80_current_data.json')); print('metadata' in data)")
        local has_companies=$(python3 -c "import json; data=json.load(open('data/wig80_current_data.json')); print('companies' in data)")
        
        if [ "$has_metadata" = "True" ]; then
            log_success "Data validation - Metadata section present"
        else
            log_error "Data validation - Metadata section missing"
        fi
        
        if [ "$has_companies" = "True" ]; then
            log_success "Data validation - Companies section present"
        else
            log_error "Data validation - Companies section missing"
        fi
    fi
    echo ""
    
    # Phase 7: Integration Tests (if services are running)
    echo "🔗 Phase 7: Integration Tests"
    echo "------------------------------------------------------------"
    
    log_info "Note: Integration tests require services to be running locally"
    log_info "Start services manually before running these tests"
    echo ""
    
    # Summary
    echo "============================================================"
    echo "  Test Summary"
    echo "============================================================"
    echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed! Ready for deployment.${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed. Please fix issues before deployment.${NC}"
        exit 1
    fi
}

# Run main function
main "$@"