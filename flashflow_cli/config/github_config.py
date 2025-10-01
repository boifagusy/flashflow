# FlashFlow GitHub Integration Configuration Example
#
# This file shows how to configure GitHub CI/CD integration for your FlashFlow project.
# You can customize these settings according to your needs.

# GitHub Repository Settings
GITHUB_REPO_SETTINGS = {
    "auto_init": True,
    "gitignore_template": "Node",
    "license_template": "mit",
    "allow_squash_merge": True,
    "allow_merge_commit": True,
    "allow_rebase_merge": False,
    "delete_branch_on_merge": True
}

# CI/CD Pipeline Configuration
PIPELINE_CONFIG = {
    "node_version": "18",
    "php_version": "8.1",
    "python_version": "3.9",
    "test_databases": ["mysql", "postgresql", "sqlite"],
    "enable_code_coverage": True,
    "deploy_on_main_only": True
}

# Mobile Build Configuration
MOBILE_BUILD_CONFIG = {
    "ios": {
        "xcode_version": "14.3",
        "ios_deployment_target": "13.0",
        "build_configurations": ["Debug", "Release", "App Store"],
        "distribution_methods": ["development", "ad-hoc", "app-store"]
    },
    "android": {
        "gradle_version": "7.6",
        "android_compile_sdk": "33",
        "android_min_sdk": "21",
        "android_target_sdk": "33",
        "build_types": ["debug", "release"]
    }
}

# Deployment Targets
DEPLOYMENT_TARGETS = {
    "web": {
        "vercel": {
            "framework": "react",
            "build_command": "npm run build",
            "output_directory": "dist"
        },
        "netlify": {
            "build_command": "npm run build",
            "publish_directory": "dist"
        }
    },
    "api": {
        "heroku": {
            "buildpack": "heroku/php",
            "php_version": "8.1"
        },
        "railway": {
            "dockerfile": "Dockerfile.api"
        }
    }
}

# Security Settings
SECURITY_CONFIG = {
    "enable_dependabot": True,
    "enable_security_advisories": True,
    "enable_code_scanning": True,
    "secrets_scanning": True,
    "vulnerability_alerts": True
}

# Environment Variables (will be stored as GitHub secrets)
REQUIRED_SECRETS = {
    # Mobile App Signing
    "APPLE_TEAM_ID": "Your Apple Developer Team ID",
    "APPLE_SIGNING_CERTIFICATE": "Base64 encoded .p12 certificate",
    "APPLE_PROVISIONING_PROFILE": "Base64 encoded provisioning profile",
    "APPLE_AUTH_KEY": "Base64 encoded App Store Connect API key",
    "APPLE_AUTH_KEY_ID": "App Store Connect API Key ID",
    "APPLE_AUTH_ISSUER_ID": "App Store Connect Issuer ID",
    
    "ANDROID_KEYSTORE": "Base64 encoded keystore file",
    "ANDROID_KEYSTORE_PASSWORD": "Keystore password",
    "ANDROID_KEY_ALIAS": "Key alias",
    "ANDROID_KEY_PASSWORD": "Key password",
    
    "GOOGLE_PLAY_SERVICE_ACCOUNT": "Base64 encoded service account JSON",
    
    # Deployment Services
    "VERCEL_TOKEN": "Vercel deployment token",
    "VERCEL_ORG_ID": "Vercel organization ID",
    "VERCEL_PROJECT_ID": "Vercel project ID",
    
    "NETLIFY_AUTH_TOKEN": "Netlify authentication token",
    "NETLIFY_SITE_ID": "Netlify site ID",
    
    "HEROKU_API_KEY": "Heroku API key",
    "HEROKU_EMAIL": "Heroku account email",
    
    "RAILWAY_TOKEN": "Railway deployment token"
}

# Notification Settings
NOTIFICATION_CONFIG = {
    "slack_webhook": None,  # Set your Slack webhook URL
    "discord_webhook": None,  # Set your Discord webhook URL
    "email_on_failure": True,
    "email_on_success": False
}

# Custom Workflow Templates
CUSTOM_WORKFLOWS = {
    "performance_testing": {
        "enabled": False,
        "tools": ["lighthouse", "webpagetest"]
    },
    "security_scanning": {
        "enabled": True,
        "tools": ["snyk", "codeql"]
    },
    "e2e_testing": {
        "enabled": False,
        "framework": "playwright"
    }
}