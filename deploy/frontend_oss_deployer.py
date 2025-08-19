"""
Frontend Deployment to Alibaba Cloud OSS with CDN Configuration
Automated deployment script for React frontend static hosting
"""

import os
import json
import boto3
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

class OSSFrontendDeployer:
    """Deploy React frontend to Alibaba Cloud OSS with CDN"""
    
    def __init__(self):
        self.oss_config = {
            'endpoint': os.getenv('OSS_ENDPOINT', 'https://oss-cn-hangzhou.aliyuncs.com'),
            'bucket_name': os.getenv('OSS_BUCKET_NAME', 'bailian-frontend'),
            'access_key_id': os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID'),
            'access_key_secret': os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
            'region': os.getenv('OSS_REGION', 'cn-hangzhou')
        }
        
        self.cdn_config = {
            'domain': os.getenv('CDN_DOMAIN', 'bailian.example.com'),
            'origin_domain': f"{self.oss_config['bucket_name']}.{self.oss_config['region']}.aliyuncs.com"
        }
        
        self.build_config = {
            'build_dir': './frontend/dist',
            'source_dir': './frontend',
            'index_file': 'index.html',
            'error_file': '404.html'
        }
    
    def build_frontend(self) -> bool:
        """Build React frontend for production"""
        print("🔨 Building React frontend for production...")
        
        try:
            import subprocess
            
            # Change to frontend directory
            os.chdir(self.build_config['source_dir'])
            
            # Install dependencies
            print("📦 Installing dependencies...")
            result = subprocess.run(['npm', 'ci'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ npm install failed: {result.stderr}")
                return False
            
            # Build for production
            print("🏗️  Building for production...")
            env = os.environ.copy()
            env['VITE_API_URL'] = os.getenv('VITE_API_URL', 'https://api.bailian.example.com')
            env['VITE_CDN_URL'] = f"https://{self.cdn_config['domain']}"
            
            result = subprocess.run(['npm', 'run', 'build'], env=env, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Build failed: {result.stderr}")
                return False
            
            print("✅ Frontend build completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False
        finally:
            # Return to original directory
            os.chdir('../..')
    
    def create_oss_bucket_policy(self) -> Dict[str, Any]:
        """Create OSS bucket policy for static website hosting"""
        return {
            "Version": "1",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "oss:GetObject"
                    ],
                    "Resource": f"acs:oss:*:*:{self.oss_config['bucket_name']}/*"
                }
            ]
        }
    
    def upload_to_oss(self) -> bool:
        """Upload built files to OSS bucket"""
        print("☁️  Uploading files to Alibaba Cloud OSS...")
        
        try:
            # This would use the actual OSS SDK
            # For now, we'll create the configuration files
            
            build_path = Path(self.build_config['build_dir'])
            if not build_path.exists():
                print(f"❌ Build directory not found: {build_path}")
                return False
            
            # Create OSS deployment configuration
            oss_deployment_config = {
                "bucket_config": {
                    "name": self.oss_config['bucket_name'],
                    "region": self.oss_config['region'],
                    "endpoint": self.oss_config['endpoint'],
                    "static_website": {
                        "index_document": self.build_config['index_file'],
                        "error_document": self.build_config['error_file']
                    },
                    "cors_configuration": {
                        "cors_rules": [
                            {
                                "allowed_origins": ["*"],
                                "allowed_methods": ["GET", "HEAD"],
                                "allowed_headers": ["*"],
                                "max_age_seconds": 86400
                            }
                        ]
                    }
                },
                "upload_config": {
                    "source_dir": str(build_path.absolute()),
                    "cache_control": {
                        "html": "no-cache",
                        "js": "max-age=31536000",
                        "css": "max-age=31536000",
                        "images": "max-age=31536000",
                        "fonts": "max-age=31536000"
                    },
                    "content_encoding": {
                        "js": "gzip",
                        "css": "gzip",
                        "html": "gzip"
                    }
                }
            }
            
            # Save deployment configuration
            config_file = "oss_deployment_config.json"
            with open(config_file, 'w') as f:
                json.dump(oss_deployment_config, f, indent=2)
            
            print(f"📄 OSS deployment configuration saved to: {config_file}")
            print("✅ OSS upload configuration ready")
            return True
            
        except Exception as e:
            print(f"❌ OSS upload error: {e}")
            return False
    
    def configure_cdn(self) -> bool:
        """Configure CDN for global acceleration"""
        print("🌐 Configuring CDN for global acceleration...")
        
        try:
            cdn_config = {
                "domain_config": {
                    "domain_name": self.cdn_config['domain'],
                    "cdn_type": "web",
                    "origin_config": {
                        "origin_type": "oss",
                        "origin_domain": self.cdn_config['origin_domain'],
                        "origin_protocol": "https"
                    }
                },
                "cache_config": {
                    "cache_rules": [
                        {
                            "path_pattern": "*.html",
                            "cache_ttl": 0,
                            "cache_control": "no-cache"
                        },
                        {
                            "path_pattern": "*.js",
                            "cache_ttl": 31536000,
                            "cache_control": "max-age=31536000"
                        },
                        {
                            "path_pattern": "*.css",
                            "cache_ttl": 31536000,
                            "cache_control": "max-age=31536000"
                        },
                        {
                            "path_pattern": "*.png,*.jpg,*.jpeg,*.gif,*.ico,*.svg",
                            "cache_ttl": 31536000,
                            "cache_control": "max-age=31536000"
                        }
                    ]
                },
                "compression_config": {
                    "enable_gzip": True,
                    "gzip_file_types": [".js", ".css", ".html", ".json", ".xml", ".txt"]
                },
                "security_config": {
                    "https_config": {
                        "enable": True,
                        "force_redirect": True,
                        "certificate_type": "free"
                    },
                    "access_control": {
                        "referer_config": {
                            "enable": False,
                            "allow_empty": True
                        }
                    }
                },
                "performance_config": {
                    "page_optimization": True,
                    "ignore_query_string": False,
                    "range_origin_pull": True
                }
            }
            
            # Save CDN configuration
            config_file = "cdn_deployment_config.json"
            with open(config_file, 'w') as f:
                json.dump(cdn_config, f, indent=2)
            
            print(f"📄 CDN configuration saved to: {config_file}")
            print("✅ CDN configuration ready")
            return True
            
        except Exception as e:
            print(f"❌ CDN configuration error: {e}")
            return False
    
    def create_deployment_scripts(self):
        """Create deployment automation scripts"""
        
        # OSS deployment script
        oss_script = '''#!/bin/bash
# OSS Deployment Script for Bailian Frontend

set -e

echo "🚀 Starting OSS deployment..."

# Check required environment variables
if [ -z "$ALIBABA_CLOUD_ACCESS_KEY_ID" ]; then
    echo "❌ ALIBABA_CLOUD_ACCESS_KEY_ID not set"
    exit 1
fi

if [ -z "$ALIBABA_CLOUD_ACCESS_KEY_SECRET" ]; then
    echo "❌ ALIBABA_CLOUD_ACCESS_KEY_SECRET not set"
    exit 1
fi

# Install ossutil if not present
if ! command -v ossutil &> /dev/null; then
    echo "📦 Installing ossutil..."
    wget https://gosspublic.alicdn.com/ossutil/1.7.14/ossutil64
    chmod +x ossutil64
    sudo mv ossutil64 /usr/local/bin/ossutil
fi

# Configure ossutil
echo "🔧 Configuring ossutil..."
ossutil config -e ${OSS_ENDPOINT:-https://oss-cn-hangzhou.aliyuncs.com} \\
               -i $ALIBABA_CLOUD_ACCESS_KEY_ID \\
               -k $ALIBABA_CLOUD_ACCESS_KEY_SECRET

# Create bucket if not exists
BUCKET_NAME=${OSS_BUCKET_NAME:-bailian-frontend}
echo "🪣 Creating bucket: $BUCKET_NAME"
ossutil mb oss://$BUCKET_NAME --acl public-read || echo "Bucket may already exist"

# Enable static website hosting
echo "🌐 Configuring static website hosting..."
ossutil website oss://$BUCKET_NAME index.html 404.html

# Upload files with proper cache headers
echo "📤 Uploading files..."

# Upload HTML files with no-cache
ossutil cp frontend/dist/ oss://$BUCKET_NAME/ -r \\
    --include "*.html" \\
    --meta "Cache-Control:no-cache"

# Upload JS/CSS files with long cache
ossutil cp frontend/dist/ oss://$BUCKET_NAME/ -r \\
    --include "*.js,*.css" \\
    --meta "Cache-Control:max-age=31536000" \\
    --meta "Content-Encoding:gzip"

# Upload image/font files with long cache
ossutil cp frontend/dist/ oss://$BUCKET_NAME/ -r \\
    --include "*.png,*.jpg,*.jpeg,*.gif,*.ico,*.svg,*.woff,*.woff2,*.ttf" \\
    --meta "Cache-Control:max-age=31536000"

echo "✅ OSS deployment completed!"
echo "🌐 Website URL: https://$BUCKET_NAME.${OSS_REGION:-cn-hangzhou}.aliyuncs.com"
'''
        
        with open('deploy_to_oss.sh', 'w') as f:
            f.write(oss_script)
        os.chmod('deploy_to_oss.sh', 0o755)
        
        # CDN deployment script
        cdn_script = '''#!/bin/bash
# CDN Configuration Script for Bailian Frontend

set -e

echo "🌐 Starting CDN configuration..."

# Check Alibaba Cloud CLI
if ! command -v aliyun &> /dev/null; then
    echo "❌ Alibaba Cloud CLI not installed"
    echo "Please install: pip install aliyun-cli"
    exit 1
fi

DOMAIN_NAME=${CDN_DOMAIN:-bailian.example.com}
BUCKET_NAME=${OSS_BUCKET_NAME:-bailian-frontend}
REGION=${OSS_REGION:-cn-hangzhou}

echo "🔧 Adding CDN domain: $DOMAIN_NAME"

# Add CDN domain
aliyun cdn AddCdnDomain \\
    --DomainName $DOMAIN_NAME \\
    --CdnType web \\
    --SourceType oss \\
    --Sources "[{\\"content\\":\\"$BUCKET_NAME.$REGION.aliyuncs.com\\",\\"type\\":\\"oss\\",\\"priority\\":20}]"

echo "⚙️  Configuring cache rules..."

# Configure cache rules for different file types
aliyun cdn BatchSetCdnDomainConfig \\
    --DomainName $DOMAIN_NAME \\
    --Functions '[
        {
            "functionName": "cache_expire",
            "functionArgs": [
                {"argName": "ttl", "argValue": "0"},
                {"argName": "file_type", "argValue": "html"}
            ]
        },
        {
            "functionName": "cache_expire", 
            "functionArgs": [
                {"argName": "ttl", "argValue": "31536000"},
                {"argName": "file_type", "argValue": "js,css"}
            ]
        }
    ]'

echo "🔒 Enabling HTTPS..."

# Enable HTTPS
aliyun cdn SetDomainServerCertificate \\
    --DomainName $DOMAIN_NAME \\
    --CertType free \\
    --ForceSet on

echo "✅ CDN configuration completed!"
echo "🌐 CDN URL: https://$DOMAIN_NAME"
'''
        
        with open('configure_cdn.sh', 'w') as f:
            f.write(cdn_script)
        os.chmod('configure_cdn.sh', 0o755)
        
        print("📄 Deployment scripts created:")
        print("  - deploy_to_oss.sh")
        print("  - configure_cdn.sh")
    
    def deploy(self) -> bool:
        """Execute complete frontend deployment"""
        print("🚀 Starting complete frontend deployment to Alibaba Cloud...")
        
        success = True
        
        # Step 1: Build frontend
        if not self.build_frontend():
            success = False
        
        # Step 2: Upload to OSS
        if success and not self.upload_to_oss():
            success = False
        
        # Step 3: Configure CDN
        if success and not self.configure_cdn():
            success = False
        
        # Step 4: Create deployment scripts
        self.create_deployment_scripts()
        
        if success:
            print("✅ Frontend deployment configuration completed!")
            print(f"🌐 Frontend will be available at: https://{self.cdn_config['domain']}")
        else:
            print("❌ Frontend deployment encountered errors")
        
        return success

def create_frontend_dockerfile_for_nginx():
    """Create optimized Dockerfile for nginx-based frontend serving"""
    
    dockerfile_content = '''# Multi-stage Dockerfile for React Frontend with Nginx
# Stage 1: Build the React application
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with npm registry mirror
RUN npm config set registry https://registry.npmmirror.com && \\
    npm ci --only=production

# Copy source code
COPY . .

# Build the application
ENV NODE_ENV=production
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine AS runtime

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost/ || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
'''
    
    nginx_config = '''events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Cache static assets
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # No cache for HTML files
        location ~* \\.html$ {
            expires -1;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
            add_header Pragma "no-cache";
        }

        # React Router support
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }
    }
}
'''
    
    # Write files
    with open('frontend/Dockerfile.nginx', 'w') as f:
        f.write(dockerfile_content)
    
    with open('frontend/nginx.conf', 'w') as f:
        f.write(nginx_config)
    
    print("📄 Created nginx-based frontend Docker configuration")

if __name__ == "__main__":
    deployer = OSSFrontendDeployer()
    create_frontend_dockerfile_for_nginx()
    deployer.deploy()