# AWS Deployment Fix Guide for Embabel Agent ECS

## Overview
This document consolidates all the issues encountered during the deployment of the Embabel Agent ECS application, both for local development and AWS ECS deployment. It details the problems, investigation process, and solutions applied.

## Issue 1: Local Development - Missing Model Configuration

### Problem
The embabel-agent-ecs client application failed to start locally with the error:
```
Default LLM 'us.anthropic.claude-sonnet-4-20250514-v1:0' not found in available models: []
```

### Root Cause
The Embabel framework requires explicit Bedrock model configuration in `embabel.models.bedrock.models`, which was missing from the application. Without this configuration, the `BedrockModels` class skipped model registration, resulting in an empty model list.

### Investigation Process
1. **Initial Hypothesis**: Model naming convention issues (tried various prefixes/suffixes)
2. **Discovery**: Found `BedrockModels.kt` in embabel-agent framework
3. **Key Finding**: The class expects configuration under `embabel.models.bedrock.models`
4. **Solution Source**: Located reference configuration in embabel-agent framework

### Solution
Created `client/src/main/resources/application-bedrock.yml` with Bedrock model configurations:

```yaml
spring:
  ai:
    bedrock:
      aws:
        region: ${AWS_REGION}
        access-key: ${AWS_ACCESS_KEY_ID}
        secret-key: ${AWS_SECRET_ACCESS_KEY}

embabel:
  models:
    bedrock:
      models:
        - name: us.anthropic.claude-sonnet-4-20250514-v1:0
          knowledge-cutoff: 2025-03-01
          input-price: 3.0
          output-price: 15.0
        - name: anthropic.claude-sonnet-4-20250514-v1:0
          knowledge-cutoff: 2025-03-01
          input-price: 3.0
          output-price: 15.0
        - name: cohere.embed-english-v3
          input-price: 0.1
          output-price: 0.0
```

## Issue 2: AWS ECS Deployment - Missing Spring Profile

### Problem
The application deployed to ECS but returned 503 Service Temporarily Unavailable errors. The client service was failing with the same model error as local development.

### Root Cause
The `bedrock` Spring profile was not activated in the ECS task definition. Without this profile, BedrockModels wouldn't register any models, even though the configuration file was present in the Docker image.

### Investigation Process
1. **Initial Check**: Verified Docker image contained `application-bedrock.yml` ✅
2. **CloudWatch Logs**: Found "Bedrock models will not be queried as the 'bedrock' profile is not active"
3. **Task Definition Review**: Discovered missing `SPRING_PROFILES_ACTIVE` environment variable

### Solution
Updated `infra/services.cfn` to add Spring profile activation:
```yaml
Environment:
  - Name: SPRING_PROFILES_ACTIVE
    Value: bedrock
  - Name: AWS_REGION
    Value: !Ref AWS::Region
```

## Issue 3: IAM Permissions for Claude 4 Models

### Problem
Even with the Spring profile activated, the application couldn't access Claude 4 Sonnet models due to missing IAM permissions.

### Root Cause
The IAM role only had permissions for Claude 3.5 Sonnet, but the application was configured to use Claude 4 Sonnet.

### Solution
Updated `infra/base.cfn` with comprehensive IAM permissions:
```yaml
Policies:
  - PolicyName: BedrockInvokeAccess
    PolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Action:
            - bedrock:InvokeModel
            - bedrock:InvokeModelWithResponseStream
          Resource:
            # Claude 4 Sonnet models
            - arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-20250514-v1:0
            - arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-sonnet-4-20250514-v1:0
            # Claude 3.5 Sonnet (backward compatibility)
            - arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0
            # Cohere embedding model
            - arn:aws:bedrock:us-east-1::foundation-model/cohere.embed-english-v3
            # Wildcard for bedrock-converse
            - arn:aws:bedrock:us-east-1::foundation-model/*
```

## Issue 4: Gateway 503 Errors

### Problem
ALB returned 503 errors because no healthy targets were available in the target group.

### Root Cause
The client service tasks were failing to start due to the model configuration issues above, leaving no healthy targets for the load balancer.

### Investigation
- **ALB Status**: Active and running
- **Target Group**: Targets stuck in "initial" or "draining" states
- **ECS Service**: Client service had 0 running tasks due to startup failures

### Solution
Fixed by resolving the underlying application startup issues (Spring profile and IAM permissions).

## Key Lessons Learned

1. **Always Check Spring Profiles First**: The BedrockModels class explicitly logs whether the bedrock profile is active. This critical log message was initially overlooked.

2. **Framework Differences Matter**: Embabel requires explicit model configuration unlike Spring AI, which can discover models automatically.

3. **Configuration Hierarchy**: Embabel checks specific configuration paths that must exist (`embabel.models.bedrock.models`).

4. **Docker Image Verification**: Always verify configuration files are included in the Docker image before deployment.

5. **IAM Permissions Must Match**: Ensure IAM permissions align with the models configured in the application.

## Complete Fix Process

### For Local Development
```bash
# Ensure application-bedrock.yml exists
ls -la client/src/main/resources/application-bedrock.yml

# Run using the provided script (handles AWS credentials properly)
./run-client.sh

# Test the agent
curl -X POST http://localhost:8080/inquire \
  -H "Content-Type: application/json" \
  -d '{"question": "List employees with React skills"}'
```

### For AWS Deployment
```bash
# Deploy the updated infrastructure
cd /Users/ryanknight/projects/aws/Sample-Model-Context-Protocol-Demos/modules/embabel-agent-ecs
./infra/deploy.sh services

# Monitor deployment
./infra/deploy.sh status
aws logs tail /ecs/embabel-agent-base --follow --region us-east-1

# Test the service
./infra/test_services.sh
```

## Timeline of Issues and Fixes

1. **Local Development Issues**
   - Missing `application-bedrock.yml` prevented model registration
   - Fixed by creating the configuration file with model definitions

2. **Initial AWS Deployment**
   - Application deployed but failed to start
   - Missing Spring profile activation caused empty model list

3. **Spring Profile Fix**
   - Added `SPRING_PROFILES_ACTIVE=bedrock` to ECS task definition
   - Models still failed due to IAM permissions

4. **IAM Permissions Update**
   - Added Claude 4 Sonnet model permissions
   - Added streaming capabilities and wildcard permissions
   - Application now starts successfully

## Current Status
✅ Local development working with `./run-client.sh`  
✅ Configuration files properly included in Docker images  
✅ Spring profiles correctly activated in ECS  
✅ IAM permissions include all required models  
✅ Application deploys and runs successfully on AWS ECS  

## References
- [Embabel Agent Framework Architecture](../../../embabel-agent/ARCHITECTURE.md)
- [Infrastructure Architecture](./INFRA_ARCHITECTURE.md)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)