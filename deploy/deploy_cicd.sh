#!/bin/bash
# CI/CD Pipeline Deployment Script
set -e

echo "🚀 Deploying CI/CD Pipeline for bailian-demo..."

# Variables
export ENVIRONMENT="production"
export PROJECT_NAME="bailian-demo"

# Check prerequisites
if [ -z "$ALIBABA_CLOUD_ACCESS_KEY_ID" ] || [ -z "$ALIBABA_CLOUD_ACCESS_KEY_SECRET" ]; then
    echo "❌ Error: Alibaba Cloud credentials not set"
    exit 1
fi

# Initialize Terraform
echo "📋 Initializing Terraform..."
terraform init

# Plan pipeline deployment
echo "📊 Planning CI/CD pipeline deployment..."
terraform plan -var="environment=$ENVIRONMENT" \
               -var="project_name=$PROJECT_NAME" \
               -out=cicd-plan

# Apply pipeline configuration
echo "🏗️  Creating CI/CD pipeline..."
terraform apply cicd-plan

# Get pipeline information
PIPELINE_NAME=$(terraform output -raw pipeline_name)
REPO_URL=$(terraform output -raw repository_clone_url)
ARTIFACTS_BUCKET=$(terraform output -raw pipeline_artifacts_bucket)

echo "📋 CI/CD Pipeline deployed successfully!"
echo "Pipeline Details:"
echo "  - Pipeline Name: $PIPELINE_NAME"
echo "  - Repository URL: $REPO_URL"
echo "  - Artifacts Bucket: $ARTIFACTS_BUCKET"

# Create buildspec files
echo "📝 Creating buildspec files..."

cat > buildspec-backend.yml << 'EOF'
version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Alibaba Cloud Container Registry...
      - docker login --username=$CR_USERNAME --password=$CR_PASSWORD registry.cn-hangzhou.aliyuncs.com
      
  build:
    commands:
      - echo Building backend Docker image...
      - cd backend
      - docker build -t bailian-demo-backend:$CODEBUILD_BUILD_NUMBER .
      - docker tag bailian-demo-backend:$CODEBUILD_BUILD_NUMBER registry.cn-hangzhou.aliyuncs.com/bailian-demo-backend:$CODEBUILD_BUILD_NUMBER
      - docker tag bailian-demo-backend:$CODEBUILD_BUILD_NUMBER registry.cn-hangzhou.aliyuncs.com/bailian-demo-backend:latest
      
  post_build:
    commands:
      - echo Pushing Docker image to Container Registry...
      - docker push registry.cn-hangzhou.aliyuncs.com/bailian-demo-backend:$CODEBUILD_BUILD_NUMBER
      - docker push registry.cn-hangzhou.aliyuncs.com/bailian-demo-backend:latest
      - echo Writing image definitions file...
      - printf '[{"name":"bailian-demo-backend","imageUri":"registry.cn-hangzhou.aliyuncs.com/bailian-demo-backend:$CODEBUILD_BUILD_NUMBER"}]' > imagedefinitions.json

artifacts:
  files:
    - imagedefinitions.json
    - k8s/**/*
  name: BackendBuildArtifact

EOF

cat > buildspec-frontend.yml << 'EOF'
version: 0.2

phases:
  pre_build:
    commands:
      - echo Installing dependencies...
      - cd frontend
      - npm install
      
  build:
    commands:
      - echo Building React application...
      - npm run build
      - echo Build completed on `date`
      
  post_build:
    commands:
      - echo Preparing for OSS deployment...
      - ls -la dist/

artifacts:
  files:
    - frontend/dist/**/*
  name: FrontendBuildArtifact
  base-directory: frontend

EOF

cat > buildspec-tests.yml << 'EOF'
version: 0.2

phases:
  pre_build:
    commands:
      - echo Installing Python dependencies...
      - cd backend
      - python3 -m pip install --upgrade pip
      - pip3 install -r requirements.txt
      - pip3 install pytest pytest-asyncio aiohttp
      
  build:
    commands:
      - echo Running unit tests...
      - python3 -m pytest tests/ -v --tb=short
      - echo Running integration tests...
      - cd ../tests
      - python3 integration_testing.py
      - echo Running performance tests...
      - python3 performance_testing.py
      
  post_build:
    commands:
      - echo Test results available in test reports

artifacts:
  files:
    - "**/*test*report*.json"
    - "**/*test*report*.xml"
  name: TestResults

EOF

echo "✅ Buildspec files created!"

# Setup initial repository
echo "🔧 Setting up initial repository..."
if [ ! -d ".git" ]; then
    git init
    git remote add origin "$REPO_URL"
fi

# Add buildspec files to repository
git add buildspec-*.yml
git add deploy/
git add k8s/
git add tests/
git add backend/
git add frontend/

git commit -m "Initial CI/CD pipeline setup"
git push origin main

echo "📤 Initial code pushed to repository!"

# Test pipeline
echo "🧪 Testing pipeline..."
echo "Pipeline will automatically start after code push."
echo "Monitor pipeline status in Alibaba Cloud Console."

echo "🎉 CI/CD Pipeline deployment completed!"
echo "📋 Summary:"
echo "  - CodeCommit Repository: Created"
echo "  - CodeBuild Projects: 3 configured"
echo "  - CodePipeline: Deployed with 4 stages"
echo "  - Buildspec Files: Generated"
echo "  - Initial Code: Pushed"

echo "🔧 Next Steps:"
echo "  1. Monitor first pipeline execution"
echo "  2. Configure environment variables in CodeBuild"
echo "  3. Test automated deployment"
echo "  4. Set up notifications and monitoring"
