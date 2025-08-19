#!/usr/bin/env python3
"""
CI/CD Pipeline Configuration for Bailian Demo
Automated deployment with Alibaba Cloud CodePipeline
"""

import json
import yaml
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class PipelineStage:
    """CI/CD pipeline stage configuration"""
    name: str
    actions: List[Dict[str, Any]]

class CICDPipelineGenerator:
    """Generate comprehensive CI/CD pipeline configuration"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.project_name = "bailian-demo"
        self.region = "cn-hangzhou"
    
    def create_pipeline_stages(self) -> List[PipelineStage]:
        """Create CI/CD pipeline stages"""
        
        # Source stage
        source_stage = PipelineStage(
            name="Source",
            actions=[
                {
                    "name": "SourceAction",
                    "actionTypeId": {
                        "category": "Source",
                        "owner": "AlibabaCloud",
                        "provider": "CodeCommit",
                        "version": "1"
                    },
                    "configuration": {
                        "RepositoryName": f"{self.project_name}-repo",
                        "BranchName": "main"
                    },
                    "outputArtifacts": ["SourceArtifact"]
                }
            ]
        )
        
        # Build stage
        build_stage = PipelineStage(
            name="Build",
            actions=[
                {
                    "name": "Backend_Build",
                    "actionTypeId": {
                        "category": "Build", 
                        "owner": "AlibabaCloud",
                        "provider": "CodeBuild",
                        "version": "1"
                    },
                    "configuration": {
                        "ProjectName": f"{self.project_name}-backend-build"
                    },
                    "inputArtifacts": ["SourceArtifact"],
                    "outputArtifacts": ["BackendBuildArtifact"]
                },
                {
                    "name": "Frontend_Build",
                    "actionTypeId": {
                        "category": "Build",
                        "owner": "AlibabaCloud", 
                        "provider": "CodeBuild",
                        "version": "1"
                    },
                    "configuration": {
                        "ProjectName": f"{self.project_name}-frontend-build"
                    },
                    "inputArtifacts": ["SourceArtifact"],
                    "outputArtifacts": ["FrontendBuildArtifact"]
                }
            ]
        )
        
        # Test stage
        test_stage = PipelineStage(
            name="Test",
            actions=[
                {
                    "name": "Unit_Tests",
                    "actionTypeId": {
                        "category": "Test",
                        "owner": "AlibabaCloud",
                        "provider": "CodeBuild", 
                        "version": "1"
                    },
                    "configuration": {
                        "ProjectName": f"{self.project_name}-unit-tests"
                    },
                    "inputArtifacts": ["BackendBuildArtifact"]
                },
                {
                    "name": "Integration_Tests",
                    "actionTypeId": {
                        "category": "Test",
                        "owner": "AlibabaCloud",
                        "provider": "CodeBuild",
                        "version": "1"
                    },
                    "configuration": {
                        "ProjectName": f"{self.project_name}-integration-tests"
                    },
                    "inputArtifacts": ["BackendBuildArtifact"]
                }
            ]
        )
        
        # Deploy stage
        deploy_stage = PipelineStage(
            name="Deploy",
            actions=[
                {
                    "name": "Deploy_Infrastructure",
                    "actionTypeId": {
                        "category": "Deploy",
                        "owner": "AlibabaCloud",
                        "provider": "CodeDeploy",
                        "version": "1"
                    },
                    "configuration": {
                        "ApplicationName": f"{self.project_name}-infrastructure",
                        "DeploymentGroupName": f"{self.project_name}-infra-{self.environment}"
                    },
                    "inputArtifacts": ["SourceArtifact"]
                },
                {
                    "name": "Deploy_Backend",
                    "actionTypeId": {
                        "category": "Deploy",
                        "owner": "AlibabaCloud",
                        "provider": "ACK",
                        "version": "1"
                    },
                    "configuration": {
                        "ClusterName": f"{self.project_name}-ack-{self.environment}",
                        "ServiceName": f"{self.project_name}-backend"
                    },
                    "inputArtifacts": ["BackendBuildArtifact"]
                },
                {
                    "name": "Deploy_Frontend",
                    "actionTypeId": {
                        "category": "Deploy",
                        "owner": "AlibabaCloud",
                        "provider": "OSS",
                        "version": "1"
                    },
                    "configuration": {
                        "BucketName": f"{self.project_name}-frontend-{self.environment}",
                        "ObjectPrefix": "/"
                    },
                    "inputArtifacts": ["FrontendBuildArtifact"]
                }
            ]
        )
        
        return [source_stage, build_stage, test_stage, deploy_stage]
    
    def generate_buildspec_backend(self) -> str:
        """Generate buildspec for backend"""
        return f"""version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Alibaba Cloud Container Registry...
      - docker login --username=$CR_USERNAME --password=$CR_PASSWORD registry.{self.region}.aliyuncs.com
      
  build:
    commands:
      - echo Building backend Docker image...
      - cd backend
      - docker build -t {self.project_name}-backend:$CODEBUILD_BUILD_NUMBER .
      - docker tag {self.project_name}-backend:$CODEBUILD_BUILD_NUMBER registry.{self.region}.aliyuncs.com/{self.project_name}-backend:$CODEBUILD_BUILD_NUMBER
      - docker tag {self.project_name}-backend:$CODEBUILD_BUILD_NUMBER registry.{self.region}.aliyuncs.com/{self.project_name}-backend:latest
      
  post_build:
    commands:
      - echo Pushing Docker image to Container Registry...
      - docker push registry.{self.region}.aliyuncs.com/{self.project_name}-backend:$CODEBUILD_BUILD_NUMBER
      - docker push registry.{self.region}.aliyuncs.com/{self.project_name}-backend:latest
      - echo Writing image definitions file...
      - printf '[{{"name":"{self.project_name}-backend","imageUri":"registry.{self.region}.aliyuncs.com/{self.project_name}-backend:$CODEBUILD_BUILD_NUMBER"}}]' > imagedefinitions.json

artifacts:
  files:
    - imagedefinitions.json
    - k8s/**/*
  name: BackendBuildArtifact
"""
    
    def generate_buildspec_frontend(self) -> str:
        """Generate buildspec for frontend"""
        return f"""version: 0.2

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
"""
    
    def generate_buildspec_tests(self) -> str:
        """Generate buildspec for testing"""
        return f"""version: 0.2

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
"""
    
    def generate_terraform_config(self) -> str:
        """Generate Terraform configuration for CI/CD pipeline"""
        stages = self.create_pipeline_stages()
        
        terraform_config = f"""
# CI/CD Pipeline Configuration
terraform {{
  required_providers {{
    alicloud = {{
      source  = "aliyun/alicloud"
      version = "~> 1.190.0"
    }}
  }}
}}

# Variables
variable "environment" {{
  description = "Environment name"
  type        = string
  default     = "{self.environment}"
}}

variable "project_name" {{
  description = "Project name"
  type        = string
  default     = "{self.project_name}"
}}

# CodeCommit Repository
resource "alicloud_code_repository" "main" {{
  repository_name = "${{var.project_name}}-repo"
  description     = "Main repository for ${{var.project_name}}"
}}

# CodeBuild Projects
resource "alicloud_codebuild_project" "backend_build" {{
  name          = "${{var.project_name}}-backend-build"
  description   = "Backend build project"
  service_role  = alicloud_ram_role.codebuild_role.arn
  
  artifacts {{
    type = "CODEPIPELINE"
  }}
  
  environment {{
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "ubuntu:20.04"
    type         = "LINUX_CONTAINER"
    
    environment_variable {{
      name  = "CR_USERNAME"
      value = "codebuild-cr-user"
    }}
    
    environment_variable {{
      name  = "CR_PASSWORD"
      value = "codebuild-cr-password"
      type  = "PARAMETER_STORE"
    }}
  }}
  
  source {{
    type      = "CODEPIPELINE"
    buildspec = "buildspec-backend.yml"
  }}
  
  tags = {{
    Environment = var.environment
    Project     = var.project_name
  }}
}}

resource "alicloud_codebuild_project" "frontend_build" {{
  name          = "${{var.project_name}}-frontend-build"
  description   = "Frontend build project"
  service_role  = alicloud_ram_role.codebuild_role.arn
  
  artifacts {{
    type = "CODEPIPELINE"
  }}
  
  environment {{
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "node:16"
    type         = "LINUX_CONTAINER"
  }}
  
  source {{
    type      = "CODEPIPELINE"
    buildspec = "buildspec-frontend.yml"
  }}
  
  tags = {{
    Environment = var.environment
    Project     = var.project_name
  }}
}}

resource "alicloud_codebuild_project" "tests" {{
  name          = "${{var.project_name}}-tests"
  description   = "Testing project"
  service_role  = alicloud_ram_role.codebuild_role.arn
  
  artifacts {{
    type = "CODEPIPELINE"
  }}
  
  environment {{
    compute_type = "BUILD_GENERAL1_MEDIUM"
    image        = "python:3.9"
    type         = "LINUX_CONTAINER"
    
    environment_variable {{
      name  = "API_BASE_URL"
      value = "http://test-alb-endpoint.com"
    }}
  }}
  
  source {{
    type      = "CODEPIPELINE"
    buildspec = "buildspec-tests.yml"
  }}
  
  tags = {{
    Environment = var.environment
    Project     = var.project_name
  }}
}}

# CodePipeline
resource "alicloud_codepipeline_pipeline" "main" {{
  pipeline_name = "${{var.project_name}}-pipeline-${{var.environment}}"
  role_arn      = alicloud_ram_role.codepipeline_role.arn
  
  artifact_store {{
    type     = "OSS"
    location = alicloud_oss_bucket.pipeline_artifacts.bucket
  }}
"""

        # Generate pipeline stages
        for i, stage in enumerate(stages):
            terraform_config += f"""
  stage {{
    name = "{stage.name}"
"""
            for j, action in enumerate(stage.actions):
                terraform_config += f"""
    action {{
      name             = "{action['name']}"
      category         = "{action['actionTypeId']['category']}"
      owner           = "{action['actionTypeId']['owner']}"
      provider        = "{action['actionTypeId']['provider']}"
      version         = "{action['actionTypeId']['version']}"
      
      configuration = {json.dumps(action['configuration'], indent=6)}
      
      {"input_artifacts  = " + json.dumps(action.get('inputArtifacts', [])) if action.get('inputArtifacts') else ""}
      {"output_artifacts = " + json.dumps(action.get('outputArtifacts', [])) if action.get('outputArtifacts') else ""}
    }}
"""
            terraform_config += "  }\n"
        
        terraform_config += """
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# OSS Bucket for Pipeline Artifacts
resource "alicloud_oss_bucket" "pipeline_artifacts" {
  bucket = "${var.project_name}-pipeline-artifacts-${var.environment}"
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# RAM Roles for CodePipeline and CodeBuild
resource "alicloud_ram_role" "codepipeline_role" {
  name        = "${var.project_name}-codepipeline-role"
  document    = jsonencode({
    Version = "1"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = ["codepipeline.aliyuncs.com"]
        }
        Action = ["sts:AssumeRole"]
      }
    ]
  })
  description = "CodePipeline service role"
}

resource "alicloud_ram_role" "codebuild_role" {
  name        = "${var.project_name}-codebuild-role"
  document    = jsonencode({
    Version = "1"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = ["codebuild.aliyuncs.com"]
        }
        Action = ["sts:AssumeRole"]
      }
    ]
  })
  description = "CodeBuild service role"
}

# Policy Attachments
resource "alicloud_ram_role_policy_attachment" "codepipeline_policy" {
  role_name   = alicloud_ram_role.codepipeline_role.name
  policy_name = "AliyunCodePipelineFullAccess"
  policy_type = "System"
}

resource "alicloud_ram_role_policy_attachment" "codebuild_policy" {
  role_name   = alicloud_ram_role.codebuild_role.name
  policy_name = "AliyunCodeBuildFullAccess"
  policy_type = "System"
}

# Outputs
output "pipeline_name" {
  description = "CodePipeline name"
  value       = alicloud_codepipeline_pipeline.main.pipeline_name
}

output "repository_clone_url" {
  description = "CodeCommit repository clone URL"
  value       = alicloud_code_repository.main.clone_url_http
}

output "pipeline_artifacts_bucket" {
  description = "Pipeline artifacts bucket"
  value       = alicloud_oss_bucket.pipeline_artifacts.bucket
}
"""
        
        return terraform_config
    
    def generate_deployment_script(self) -> str:
        """Generate CI/CD deployment script"""
        return f"""#!/bin/bash
# CI/CD Pipeline Deployment Script
set -e

echo "🚀 Deploying CI/CD Pipeline for {self.project_name}..."

# Variables
export ENVIRONMENT="{self.environment}"
export PROJECT_NAME="{self.project_name}"

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
terraform plan -var="environment=$ENVIRONMENT" \\
               -var="project_name=$PROJECT_NAME" \\
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
{self.generate_buildspec_backend()}
EOF

cat > buildspec-frontend.yml << 'EOF'
{self.generate_buildspec_frontend()}
EOF

cat > buildspec-tests.yml << 'EOF'
{self.generate_buildspec_tests()}
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
"""

def main():
    """Generate CI/CD pipeline configuration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate CI/CD pipeline configuration")
    parser.add_argument("--environment", default="production", help="Environment name")
    
    args = parser.parse_args()
    
    generator = CICDPipelineGenerator(args.environment)
    
    # Generate configurations
    terraform_config = generator.generate_terraform_config()
    deployment_script = generator.generate_deployment_script()
    
    # Save configurations
    with open("cicd_terraform.tf", "w") as f:
        f.write(terraform_config)
    
    with open("deploy_cicd.sh", "w") as f:
        f.write(deployment_script)
    
    # Generate individual buildspec files
    with open("buildspec-backend.yml", "w") as f:
        f.write(generator.generate_buildspec_backend())
    
    with open("buildspec-frontend.yml", "w") as f:
        f.write(generator.generate_buildspec_frontend())
    
    with open("buildspec-tests.yml", "w") as f:
        f.write(generator.generate_buildspec_tests())
    
    # Make deployment script executable
    import os
    os.chmod("deploy_cicd.sh", 0o755)
    
    print("✅ CI/CD pipeline files generated:")
    print("  - cicd_terraform.tf (Terraform configuration)")
    print("  - deploy_cicd.sh (Deployment script)")
    print("  - buildspec-backend.yml (Backend build)")
    print("  - buildspec-frontend.yml (Frontend build)")
    print("  - buildspec-tests.yml (Testing)")
    print(f"  - Environment: {args.environment}")

if __name__ == "__main__":
    main()