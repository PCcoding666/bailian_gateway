
# CI/CD Pipeline Configuration
terraform {
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "~> 1.190.0"
    }
  }
}

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "bailian-demo"
}

# CodeCommit Repository
resource "alicloud_code_repository" "main" {
  repository_name = "${var.project_name}-repo"
  description     = "Main repository for ${var.project_name}"
}

# CodeBuild Projects
resource "alicloud_codebuild_project" "backend_build" {
  name          = "${var.project_name}-backend-build"
  description   = "Backend build project"
  service_role  = alicloud_ram_role.codebuild_role.arn
  
  artifacts {
    type = "CODEPIPELINE"
  }
  
  environment {
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "ubuntu:20.04"
    type         = "LINUX_CONTAINER"
    
    environment_variable {
      name  = "CR_USERNAME"
      value = "codebuild-cr-user"
    }
    
    environment_variable {
      name  = "CR_PASSWORD"
      value = "codebuild-cr-password"
      type  = "PARAMETER_STORE"
    }
  }
  
  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec-backend.yml"
  }
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "alicloud_codebuild_project" "frontend_build" {
  name          = "${var.project_name}-frontend-build"
  description   = "Frontend build project"
  service_role  = alicloud_ram_role.codebuild_role.arn
  
  artifacts {
    type = "CODEPIPELINE"
  }
  
  environment {
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "node:16"
    type         = "LINUX_CONTAINER"
  }
  
  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec-frontend.yml"
  }
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "alicloud_codebuild_project" "tests" {
  name          = "${var.project_name}-tests"
  description   = "Testing project"
  service_role  = alicloud_ram_role.codebuild_role.arn
  
  artifacts {
    type = "CODEPIPELINE"
  }
  
  environment {
    compute_type = "BUILD_GENERAL1_MEDIUM"
    image        = "python:3.9"
    type         = "LINUX_CONTAINER"
    
    environment_variable {
      name  = "API_BASE_URL"
      value = "http://test-alb-endpoint.com"
    }
  }
  
  source {
    type      = "CODEPIPELINE"
    buildspec = "buildspec-tests.yml"
  }
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# CodePipeline
resource "alicloud_codepipeline_pipeline" "main" {
  pipeline_name = "${var.project_name}-pipeline-${var.environment}"
  role_arn      = alicloud_ram_role.codepipeline_role.arn
  
  artifact_store {
    type     = "OSS"
    location = alicloud_oss_bucket.pipeline_artifacts.bucket
  }

  stage {
    name = "Source"

    action {
      name             = "SourceAction"
      category         = "Source"
      owner           = "AlibabaCloud"
      provider        = "CodeCommit"
      version         = "1"
      
      configuration = {
      "RepositoryName": "bailian-demo-repo",
      "BranchName": "main"
}
      
      
      output_artifacts = ["SourceArtifact"]
    }
  }

  stage {
    name = "Build"

    action {
      name             = "Backend_Build"
      category         = "Build"
      owner           = "AlibabaCloud"
      provider        = "CodeBuild"
      version         = "1"
      
      configuration = {
      "ProjectName": "bailian-demo-backend-build"
}
      
      input_artifacts  = ["SourceArtifact"]
      output_artifacts = ["BackendBuildArtifact"]
    }

    action {
      name             = "Frontend_Build"
      category         = "Build"
      owner           = "AlibabaCloud"
      provider        = "CodeBuild"
      version         = "1"
      
      configuration = {
      "ProjectName": "bailian-demo-frontend-build"
}
      
      input_artifacts  = ["SourceArtifact"]
      output_artifacts = ["FrontendBuildArtifact"]
    }
  }

  stage {
    name = "Test"

    action {
      name             = "Unit_Tests"
      category         = "Test"
      owner           = "AlibabaCloud"
      provider        = "CodeBuild"
      version         = "1"
      
      configuration = {
      "ProjectName": "bailian-demo-unit-tests"
}
      
      input_artifacts  = ["BackendBuildArtifact"]
      
    }

    action {
      name             = "Integration_Tests"
      category         = "Test"
      owner           = "AlibabaCloud"
      provider        = "CodeBuild"
      version         = "1"
      
      configuration = {
      "ProjectName": "bailian-demo-integration-tests"
}
      
      input_artifacts  = ["BackendBuildArtifact"]
      
    }
  }

  stage {
    name = "Deploy"

    action {
      name             = "Deploy_Infrastructure"
      category         = "Deploy"
      owner           = "AlibabaCloud"
      provider        = "CodeDeploy"
      version         = "1"
      
      configuration = {
      "ApplicationName": "bailian-demo-infrastructure",
      "DeploymentGroupName": "bailian-demo-infra-production"
}
      
      input_artifacts  = ["SourceArtifact"]
      
    }

    action {
      name             = "Deploy_Backend"
      category         = "Deploy"
      owner           = "AlibabaCloud"
      provider        = "ACK"
      version         = "1"
      
      configuration = {
      "ClusterName": "bailian-demo-ack-production",
      "ServiceName": "bailian-demo-backend"
}
      
      input_artifacts  = ["BackendBuildArtifact"]
      
    }

    action {
      name             = "Deploy_Frontend"
      category         = "Deploy"
      owner           = "AlibabaCloud"
      provider        = "OSS"
      version         = "1"
      
      configuration = {
      "BucketName": "bailian-demo-frontend-production",
      "ObjectPrefix": "/"
}
      
      input_artifacts  = ["FrontendBuildArtifact"]
      
    }
  }

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
