# No-Code Architects Toolkit - AWS Lambda Deployment Guide

This guide explains how to deploy the No-Code Architects Toolkit as an AWS Lambda Application using AWS SAM.

## Prerequisites

1. **AWS CLI** installed and configured
2. **AWS SAM CLI** installed  
3. **Python 3.9** installed
4. **Docker** (for building layers)

### Install AWS SAM CLI

```bash
# macOS
brew install aws/tap/aws-sam-cli

# Linux/Windows
pip install aws-sam-cli
```

## Quick Start

### 1. Initialize and Build

```bash
# Build the application
sam build

# If you encounter dependency issues, build with container
sam build --use-container
```

### 2. Deploy

```bash
# First deployment (guided)
sam deploy --guided

# Subsequent deployments
sam deploy
```

### 3. Test the Application

After deployment, you'll get a Function URL. Test it:

```bash
curl https://your-function-url.lambda-url.region.on.aws/
```

## Detailed Deployment Steps

### Step 1: Project Structure Verification

Ensure your project has these key files:
```
├── template.yaml          # SAM template
├── lambda_handler.py      # Lambda entry point
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── config.py              # Configuration
└── layers/
    └── ffmpeg/           # FFmpeg layer (optional)
```

### Step 2: Build the Application

```bash
# Clean build
sam build --clean

# Build with verbose output
sam build --debug
```

**Note**: The build process will:
- Create a `.aws-sam/` directory
- Install Python dependencies
- Package the Lambda function

### Step 3: Deploy Configuration

During `sam deploy --guided`, you'll be prompted for:

- **Stack Name**: e.g., `no-code-toolkit-prod`
- **AWS Region**: e.g., `us-east-1`
- **Environment**: `dev`, `staging`, or `prod`
- **BucketName**: Will be auto-generated if left empty
- **Confirm changes before deploy**: `Y`
- **Allow SAM CLI IAM role creation**: `Y`
- **Save parameters to configuration file**: `Y`

### Step 4: Verify Deployment

1. **Check AWS Console**:
   - Go to Lambda → Applications
   - Find your application: `no-code-toolkit-{environment}`

2. **Check Function URL**:
   ```bash
   # Get the Function URL from CloudFormation outputs
   aws cloudformation describe-stacks \
     --stack-name no-code-toolkit-prod \
     --query 'Stacks[0].Outputs[?OutputKey==`FunctionUrl`].OutputValue' \
     --output text
   ```

3. **Test Endpoints**:
   ```bash
   # Test basic endpoint
   curl https://your-function-url/v1/toolkit/test
   
   # Test with payload
   curl -X POST https://your-function-url/v1/media/convert \
     -H "Content-Type: application/json" \
     -d '{"input": "test"}'
   ```

## Environment Variables

The application uses these environment variables (automatically set):

- `ENVIRONMENT`: Deployment environment (dev/staging/prod)
- `STORAGE_BUCKET`: S3 bucket name for file storage
- `LOCAL_STORAGE_PATH`: `/tmp` (Lambda temp directory)
- `AWS_DEFAULT_REGION`: AWS region

## Customization

### Custom Domain

To use a custom domain, add to `template.yaml`:

```yaml
Resources:
  CustomDomain:
    Type: AWS::ApiGatewayV2::DomainName
    Properties:
      DomainName: api.yourdomain.com
      DomainNameConfigurations:
        - CertificateArn: !Ref SSLCertificate
```

### Additional Resources

Add more AWS resources as needed:

```yaml
Resources:
  # DynamoDB for job tracking
  JobsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "toolkit-jobs-${Environment}"
      
  # SQS for async processing
  ProcessingQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "toolkit-queue-${Environment}"
```

## Monitoring

### CloudWatch Logs

View logs:
```bash
sam logs --stack-name no-code-toolkit-prod --tail
```

### CloudWatch Metrics

The application automatically creates metrics for:
- Function invocations
- Error rates
- Duration
- Memory usage

## Troubleshooting

### Common Issues

1. **Build Failures**:
   ```bash
   # Use container build for dependency issues
   sam build --use-container
   ```

2. **Permission Errors**:
   - Ensure your AWS credentials have sufficient permissions
   - Check IAM roles in the template

3. **Memory/Timeout Issues**:
   - Increase `MemorySize` and `Timeout` in template.yaml
   - Monitor CloudWatch for memory usage

4. **S3 Access Issues**:
   - Verify bucket permissions
   - Check bucket name uniqueness

### Debugging

```bash
# Local testing
sam local start-api --debug

# Invoke specific function
sam local invoke NoCodeToolkitFunction --event events/test-event.json
```

### Logs

```bash
# Tail logs
sam logs --name NoCodeToolkitFunction --stack-name no-code-toolkit-prod --tail

# Get specific time range
sam logs --name NoCodeToolkitFunction --stack-name no-code-toolkit-prod \
  --start-time '10min ago' --end-time '1min ago'
```

## Cleanup

To remove the entire application:

```bash
sam delete --stack-name no-code-toolkit-prod
```

## Production Considerations

1. **Security**: 
   - Enable authentication on Function URL
   - Use VPC for sensitive operations
   - Implement rate limiting

2. **Scaling**:
   - Monitor concurrent executions
   - Set reserved concurrency if needed
   - Consider using Application Load Balancer for high traffic

3. **Cost Optimization**:
   - Monitor Lambda costs in AWS Cost Explorer
   - Optimize memory allocation based on actual usage
   - Use S3 lifecycle policies for storage

4. **Backup**:
   - Version your Lambda functions
   - Backup S3 bucket contents
   - Version your SAM templates in git

## Next Steps

- Set up CI/CD pipeline with GitHub Actions
- Implement monitoring and alerting
- Add more endpoints as needed
- Configure custom domain
- Set up staging environment