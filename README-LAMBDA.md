# No-Code Architects Toolkit - AWS Lambda Application

🚀 **Media processing toolkit deployed as AWS Lambda Application with SAM**

This repository has been converted from a Flask web application to an AWS Lambda Application that can be deployed using AWS Serverless Application Model (SAM).

## 🎯 What's New

✅ **AWS SAM Template** (`template.yaml`) - Complete infrastructure as code  
✅ **Lambda Handler** (`lambda_handler.py`) - Flask-to-Lambda adapter  
✅ **S3 Integration** - Automatic bucket creation and permissions  
✅ **Function URL** - Direct HTTPS access to your application  
✅ **IAM Roles** - Proper security permissions  
✅ **One-Click Deployment** - Simple deployment script  

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Function URL  │───▶│  Lambda Function │───▶│   S3 Bucket     │
│   (HTTPS API)   │    │  (Flask App)     │    │ (Media Storage) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  CloudWatch     │
                       │  (Logs/Metrics) │
                       └─────────────────┘
```

## 🚀 Quick Deploy

### Prerequisites
- AWS CLI configured
- AWS SAM CLI installed
- Python 3.9+
- Docker (optional, for container builds)

### Deploy in 3 Steps

```bash
# 1. Build the application
sam build

# 2. Deploy with guided setup
sam deploy --guided

# 3. Or use the deployment script
./deploy.sh prod
```

### Deploy to Different Environments

```bash
./deploy.sh dev      # Development environment
./deploy.sh staging  # Staging environment  
./deploy.sh prod     # Production environment
```

## 📋 What Gets Created

When you deploy, AWS creates:

| Resource | Purpose |
|----------|---------|
| **Lambda Function** | Main application (Flask app) |
| **S3 Bucket** | Media file storage |
| **IAM Role** | Permissions for Lambda |
| **Function URL** | HTTPS endpoint for API |
| **CloudWatch Logs** | Application logging |
| **CloudFormation Stack** | Infrastructure management |

## 🌐 Access Your Application

After deployment, you'll get a Function URL like:
```
https://abcd1234.lambda-url.us-east-1.on.aws/
```

Test endpoints:
```bash
# Health check
curl https://your-function-url/v1/toolkit/test

# Media endpoints
curl https://your-function-url/v1/media/convert
curl https://your-function-url/v1/video/thumbnail
```

## 📊 Monitoring & Debugging

### View Logs
```bash
# Real-time logs
sam logs --stack-name no-code-toolkit-prod --tail

# Specific function logs
aws logs tail /aws/lambda/no-code-toolkit-prod --follow
```

### Local Testing
```bash
# Start local API
sam local start-api

# Test specific function
sam local invoke NoCodeToolkitFunction --event events/test-event.json
```

### AWS Console

Navigate to: **AWS Console → Lambda → Applications → no-code-toolkit-{env}**

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `prod` |
| `STORAGE_BUCKET` | S3 bucket name | `no-code-toolkit-prod-123456` |
| `LOCAL_STORAGE_PATH` | Temp directory | `/tmp` |
| `AWS_DEFAULT_REGION` | AWS region | `us-east-1` |

### Customization

Edit `template.yaml` to:
- Change memory/timeout settings
- Add new AWS resources
- Modify IAM permissions
- Configure custom domains

### Multiple Environments

The template supports multiple environments:
- **dev**: Development with relaxed settings
- **staging**: Pre-production testing
- **prod**: Production with optimized settings

## 💰 Cost Estimation

| Component | Estimated Monthly Cost* |
|-----------|-------------------------|
| Lambda (1M requests) | $0.20 |
| S3 Storage (10GB) | $0.23 |
| CloudWatch Logs | $0.50 |
| **Total** | **~$1.00/month** |

*Costs vary by usage and region

## 🛠️ Development Workflow

### 1. Local Development
```bash
# Start local API server
sam local start-api --debug

# Your app runs at http://localhost:3000
```

### 2. Make Changes
- Edit Python code
- Update `template.yaml` for infrastructure changes
- Test locally

### 3. Deploy Changes
```bash
# Quick deployment
./deploy.sh dev

# Production deployment
./deploy.sh prod
```

## 🔐 Security Features

✅ **IAM Least Privilege** - Minimal required permissions  
✅ **S3 Bucket Encryption** - Data encrypted at rest  
✅ **VPC Support** - Can be deployed in private network  
✅ **HTTPS Only** - All traffic encrypted in transit  
✅ **CloudWatch Monitoring** - Full observability  

## 📈 Scaling

The Lambda application automatically scales:
- **Concurrent Executions**: Up to 1000 (default)
- **Memory**: 128MB - 10GB configurable
- **Timeout**: Up to 15 minutes
- **Storage**: /tmp up to 10GB

## 🗑️ Cleanup

Remove everything:
```bash
sam delete --stack-name no-code-toolkit-prod
```

## 📚 Learn More

- [📖 Detailed Deployment Guide](./DEPLOYMENT.md)
- [🏗️ SAM Template Reference](./template.yaml)
- [🔧 Lambda Handler Code](./lambda_handler.py)
- [⚙️ Configuration Options](./samconfig.toml)

## 🤝 Migration from Flask

This project was migrated from a Flask web application to Lambda. Key changes:

1. **Added `lambda_handler.py`** - WSGI-to-Lambda adapter
2. **Created `template.yaml`** - Infrastructure definition
3. **Updated `config.py`** - Lambda-compatible configuration
4. **Added deployment scripts** - Automated deployment

The original Flask code remains unchanged and fully functional.

## 💡 Next Steps

- [ ] Set up CI/CD pipeline
- [ ] Configure custom domain
- [ ] Add CloudFront for caching
- [ ] Implement API authentication
- [ ] Add monitoring dashboards
- [ ] Scale to multiple regions

---

**🎉 Your Flask app is now a serverless Lambda application!**