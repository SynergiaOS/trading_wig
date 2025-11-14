# Railway Rollback Procedures

## 🎯 Overview
This document provides step-by-step procedures for rolling back Railway deployments when issues are detected. It covers different rollback scenarios and best practices for minimizing downtime.

---

## 🚨 When to Rollback

### Immediate Rollback Triggers
- **SEV 1 Incident**: Complete service outage affecting all users
- **Data Corruption**: Production data being corrupted or lost
- **Security Vulnerability**: Critical security issue introduced
- **Performance Degradation**: Response times increased by > 500%
- **Functionality Loss**: Core features completely broken

### Consider Rollback
- **SEV 2 Incident**: Major functionality impaired
- **Increased Error Rate**: Error rate > 5% sustained
- **Partial Outage**: Single service down in multi-service setup
- **Data Freshness Issues**: Data not updating for > 1 hour

### Do Not Rollback (Fix Forward Instead)
- **Minor UI Issues**: Cosmetic problems not affecting functionality
- **Performance < 100% degradation**: Acceptable performance impact
- **Feature Flags**: Issues that can be disabled via configuration
- **Documentation**: Documentation or non-code issues

---

## 📋 Pre-Rollback Checklist

### Before Initiating Rollback

- [ ] **Identify the Issue**: Confirm the problem is deployment-related
- [ ] **Assess Impact**: Determine how many users are affected
- [ ] **Check Previous Version**: Verify previous version was stable
- [ ] **Notify Stakeholders**: Inform team and stakeholders
- [ ] **Document Current State**: Take screenshots of metrics/logs
- [ ] **Backup Current State**: Export logs and metrics if possible

### Rollback Decision Matrix

| Issue Type | Severity | Users Affected | Rollback? | Alternative |
|------------|----------|----------------|-----------|-------------|
| Complete outage | Critical | 100% | ✅ Yes | - |
| Major feature broken | High | > 50% | ✅ Yes | Feature flag |
| Performance degraded | Medium | > 30% | ⚠️ Consider | Optimize |
| Minor bug | Low | < 10% | ❌ No | Hotfix |
| UI glitch | Minimal | < 5% | ❌ No | Next deploy |

---

## 🔄 Rollback Procedures

### Method 1: Railway Dashboard (Recommended)

**Step-by-Step Procedure:**

1. **Access Railway Dashboard**
   ```bash
   # Navigate to:
   https://railway.app/project/[project-id]
   ```

2. **Select Service to Rollback**
   - Click on the affected service (frontend/backend/analysis)
   - Navigate to "Deployments" tab

3. **Identify Previous Working Deployment**
   - Review deployment history
   - Find last known good deployment (check timestamp)
   - Verify it was successful (green checkmark)

4. **Initiate Rollback**
   - Click on the previous deployment
   - Click "Rollback" button
   - Confirm rollback when prompted

5. **Monitor Rollback Progress**
   - Watch deployment logs
   - Monitor service status
   - Check health check results

6. **Verify Service Health**
   ```bash
   # Test service endpoints
   curl https://service-name.railway.app/health-endpoint
   
   # Check logs for errors
   # Review metrics for anomalies
   ```

7. **Update Stakeholders**
   - Confirm rollback successful
   - Provide updated ETA for full resolution
   - Schedule post-mortem if needed

**Expected Timeline**: 2-5 minutes per service

---

### Method 2: Railway CLI

**Prerequisites:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link
```

**Rollback Procedure:**

1. **List Deployments**
   ```bash
   railway deployments
   
   # Output:
   # ID          Status    Created At          Trigger
   # dep_xxx     SUCCESS   2025-11-08 10:00    GitHub
   # dep_yyy     SUCCESS   2025-11-08 09:30    GitHub
   # dep_zzz     FAILED    2025-11-08 09:00    GitHub
   ```

2. **Identify Deployment ID**
   - Find ID of last working deployment
   - Copy the deployment ID (e.g., `dep_yyy`)

3. **Execute Rollback**
   ```bash
   railway rollback dep_yyy
   
   # Or use interactive selection
   railway rollback
   ```

4. **Monitor Progress**
   ```bash
   # Watch logs
   railway logs
   
   # Check status
   railway status
   ```

5. **Verify Rollback**
   ```bash
   # Test endpoints
   curl https://service-name.railway.app/data
   
   # Check deployment list to confirm rollback deployment
   railway deployments
   ```

**Expected Timeline**: 3-6 minutes per service

---

### Method 3: Git-based Rollback (Advanced)

**Use Case**: When you need to rollback code and trigger new deployment

**Procedure:**

1. **Identify Commit to Rollback To**
   ```bash
   # View git history
   git log --oneline -10
   
   # Find last known good commit
   # Copy commit hash
   ```

2. **Create Rollback Branch**
   ```bash
   # Create rollback branch
   git checkout -b rollback/[date]-[issue]
   
   # Reset to good commit
   git reset --hard [commit-hash]
   ```

3. **Tag for Identification**
   ```bash
   # Create rollback tag
   git tag -a rollback/[version] -m "Rollback due to [issue]"
   ```

4. **Force Push to Trigger Deployment**
   ```bash
   # Push rollback branch
   git push origin rollback/[date]-[issue]
   
   # Or force push to main (use with caution)
   # git push --force origin main
   ```

5. **Monitor Deployment**
   ```bash
   # Watch Railway dashboard
   # Verify new deployment is successful
   ```

6. **Document Rollback**
   ```bash
   # Create rollback commit
   git commit --allow-empty -m "Rollback: [reason] - Previous: [commit-hash]"
   ```

**⚠️ Warning**: Force push can disrupt other developers. Use only in emergencies.

---

## 🎯 Multi-Service Rollback Strategy

### Scenario: All Services Affected

**Recommended Order**: Rollback in reverse dependency order

1. **Analysis API** (no dependencies)
2. **Backend API** (depends on Analysis)
3. **Frontend** (depends on both APIs)

**Procedure:**
```bash
# Rollback each service sequentially
# Wait for each to be healthy before proceeding

# Step 1: Rollback Analysis
railway service analysis
railway rollback dep_xxx

# Wait and verify
sleep 60
curl https://analysis-service.railway.app/api/analysis

# Step 2: Rollback Backend
railway service backend
railway rollback dep_yyy

# Wait and verify
sleep 60
curl https://backend-service.railway.app/data

# Step 3: Rollback Frontend
railway service frontend
railway rollback dep_zzz

# Wait and verify
sleep 60
curl https://frontend-service.railway.app/
```

**Total Expected Time**: 8-15 minutes

---

### Scenario: Single Service Affected

**Procedure:**
```bash
# Rollback only affected service
railway service [affected-service]
railway rollback [deployment-id]

# Verify other services still work
curl https://backend-service.railway.app/data
curl https://analysis-service.railway.app/api/analysis
curl https://frontend-service.railway.app/
```

**Expected Time**: 2-5 minutes

---

## 📝 Post-Rollback Checklist

### Immediate Verification (0-5 minutes)

- [ ] **Service Status**: All services show "Healthy" in Railway
- [ ] **Endpoint Testing**: All critical endpoints respond correctly
- [ ] **Error Rates**: Error rates returned to normal levels
- [ ] **Response Times**: Performance back to acceptable levels
- [ ] **User Impact**: Confirm users can access the application

### Short-term Monitoring (5-30 minutes)

- [ ] **Log Review**: Check for errors in rollback deployment
- [ ] **Metrics Analysis**: Verify resource usage is normal
- [ ] **User Feedback**: Monitor for user-reported issues
- [ ] **Data Integrity**: Verify data is loading correctly

### Documentation (30-60 minutes)

- [ ] **Incident Report**: Document what happened
- [ ] **Rollback Record**: Record which version was rolled back to
- [ ] **Lessons Learned**: Identify root cause and prevention
- [ ] **Communication**: Update stakeholders on resolution

---

## 🔄 Rollback Validation

### Automated Validation Script

```bash
#!/bin/bash
# rollback-validation.sh

FRONTEND_URL="https://frontend-service.railway.app"
BACKEND_URL="https://backend-service.railway.app"
ANALYSIS_URL="https://analysis-service.railway.app"

echo "🔍 Validating rollback..."

# Test frontend
echo "Testing frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL)
if [ $FRONTEND_STATUS -eq 200 ]; then
    echo "✅ Frontend: OK"
else
    echo "❌ Frontend: FAILED (Status: $FRONTEND_STATUS)"
fi

# Test backend
echo "Testing backend..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/data)
if [ $BACKEND_STATUS -eq 200 ]; then
    echo "✅ Backend: OK"
else
    echo "❌ Backend: FAILED (Status: $BACKEND_STATUS)"
fi

# Test analysis
echo "Testing analysis..."
ANALYSIS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $ANALYSIS_URL/api/analysis)
if [ $ANALYSIS_STATUS -eq 200 ]; then
    echo "✅ Analysis: OK"
else
    echo "❌ Analysis: FAILED (Status: $ANALYSIS_STATUS)"
fi

echo "Rollback validation complete!"
```

**Usage**: Run after rollback to verify success

---

## 🛡️ Rollback Best Practices

### 1. Preparation
- **Keep previous deployments**: Railway retains last 10 deployments
- **Test rollbacks**: Practice in staging environment
- **Document dependencies**: Know service relationships
- **Maintain runbooks**: Keep procedures up to date

### 2. During Rollback
- **Stay calm**: Follow procedures methodically
- **Communicate**: Keep team informed
- **Monitor closely**: Watch metrics and logs
- **Document everything**: Record timestamps and actions

### 3. After Rollback
- **Verify thoroughly**: Don't assume success
- **Investigate root cause**: Prevent recurrence
- **Update procedures**: Improve based on experience
- **Conduct post-mortem**: Learn from the incident

### 4. Prevention
- **Staging deployments**: Test before production
- **Gradual rollouts**: Deploy to subset of users first
- **Feature flags**: Enable easy disabling of features
- **Automated testing**: Catch issues before deployment

---

## 📊 Rollback Metrics

### Track These Metrics
- **Rollback Frequency**: How often rollbacks occur
- **Time to Detect**: How quickly issues are identified
- **Time to Rollback**: How long rollback takes
- **Rollback Success Rate**: Percentage of successful rollbacks
- **User Impact Duration**: How long users are affected

### Targets
- **Rollback Frequency**: < 5% of deployments
- **Time to Detect**: < 5 minutes
- **Time to Rollback**: < 10 minutes
- **Rollback Success Rate**: > 95%
- **User Impact Duration**: < 15 minutes

---

## 🎯 Emergency Contacts

### Escalation Path
1. **On-call Engineer**: Primary responder
2. **Tech Lead**: Technical decisions
3. **DevOps Team**: Infrastructure issues
4. **Railway Support**: Platform issues (paid plans)

### Contact Information
```yaml
Role: On-call Engineer
Slack: #incidents
Phone: [On-call rotation]

Role: Tech Lead
Slack: @tech-lead
Email: tech-lead@company.com

Role: Railway Support
Method: Dashboard → Help → Contact Support
Hours: 24/7 (paid plans)
```

---

## 📚 Additional Resources

- [Railway Deployment Documentation](https://docs.railway.app/deployments)
- [Railway CLI Reference](https://docs.railway.app/cli)
- [Incident Response Best Practices](https://www.atlassian.com/incident-management)
- [Postmortem Template](./incident-postmortem-template.md)

---

**Last Updated**: 2025-11-08
**Version**: 1.0
**Maintained By**: DevOps Team
**Next Review**: 2025-12-08