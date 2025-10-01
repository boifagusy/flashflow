# FlashFlow GitHub CI/CD Integration

FlashFlow provides seamless integration with GitHub Actions for continuous integration and continuous deployment (CI/CD). This feature automates the entire build, test, and deployment pipeline for your FlashFlow applications.

## Quick Start

### One-Time Setup

The GitHub integration is a one-time setup process that configures your entire CI/CD pipeline:

```bash
# Launch web-based setup wizard
flashflow setup --gui --github

# Or use CLI setup
flashflow setup --github
```

### What Happens During Setup

1. **GitHub Account Linking**: Securely connect your GitHub account using OAuth
2. **Repository Configuration**: Create a new repository or use an existing one
3. **Credential Storage**: Store Apple Developer and Android signing credentials as encrypted GitHub secrets
4. **Workflow Generation**: Automatically create GitHub Actions workflows for:
   - Continuous Integration (testing)
   - iOS app building and distribution
   - Android app building and distribution
   - Web app deployment
   - API deployment
   - Release management

## Features

### 🔄 Continuous Integration

- **Automated Testing**: Runs on every push and pull request
- **Multi-Database Testing**: Tests against MySQL, PostgreSQL, and SQLite
- **Cross-Platform**: Supports Node.js, PHP, and Python components
- **Code Coverage**: Automatic test coverage reporting
- **Quality Gates**: Prevents merging if tests fail

### 📱 Mobile App Building

#### iOS Builds
- **Automatic Code Signing**: Uses your Apple Developer certificates
- **Multiple Distribution Methods**: Development, Ad-Hoc, App Store
- **App Store Connect Integration**: Automatic uploads to TestFlight and App Store
- **Xcode Version Management**: Always uses the latest stable Xcode

#### Android Builds
- **Keystore Management**: Secure keystore handling for app signing
- **Multiple Build Types**: Debug, Release, and Play Store builds
- **Google Play Integration**: Automatic uploads to Play Console
- **AAB and APK Generation**: Supports both Android App Bundle and APK formats

### 🌐 Web Deployment

- **Multi-Platform Support**: Deploy to Vercel, Netlify, and other platforms
- **Automatic Builds**: Triggered on successful CI pipeline
- **Environment Management**: Separate staging and production deployments
- **CDN Integration**: Automatic static asset optimization

### 🔧 API Deployment

- **Backend Services**: Deploy Laravel/PHP APIs to Heroku, Railway, and other platforms
- **Database Migration**: Automatic database updates on deployment
- **Environment Configuration**: Secure environment variable management
- **Health Checks**: Automatic service health monitoring

## Workflow Files

FlashFlow creates the following GitHub Actions workflows:

### Main CI/CD Pipeline (`main.yml`)
```yaml
# Triggers on push to main/develop branches and pull requests
# Runs tests, builds application, creates deployment artifacts
```

### iOS Build Pipeline (`ios.yml`)
```yaml
# Builds iOS apps for different distribution methods
# Handles code signing and App Store Connect uploads
```

### Android Build Pipeline (`android.yml`)
```yaml
# Builds Android APKs and AABs
# Handles keystore signing and Google Play uploads
```

### Web Deployment (`deploy-web.yml`)
```yaml
# Deploys web applications to hosting platforms
# Handles asset optimization and CDN configuration
```

### API Deployment (`deploy-api.yml`)
```yaml
# Deploys backend APIs to cloud platforms
# Handles database migrations and service configuration
```

### Release Management (`release.yml`)
```yaml
# Creates releases and triggers mobile app builds
# Handles version bumping and changelog generation
```

## Security & Credentials

### Secure Credential Storage

All sensitive credentials are stored as encrypted GitHub secrets:

- **Apple Developer**: Team ID, signing certificates, provisioning profiles, API keys
- **Android**: Keystore files, passwords, key aliases
- **Deployment**: Platform tokens, API keys, service account files

### Best Practices

1. **Principle of Least Privilege**: Each secret has minimal required permissions
2. **Rotation**: Regular credential rotation reminders
3. **Audit Trail**: Complete history of secret usage
4. **Environment Separation**: Different credentials for staging and production

## Project Inheritance

Once configured, all your FlashFlow projects automatically inherit:

- **GitHub Actions Workflows**: Consistent CI/CD across projects
- **Security Credentials**: Shared Apple and Android signing credentials
- **Deployment Configuration**: Standard deployment pipelines
- **Quality Gates**: Consistent testing and quality standards

## Usage Examples

### Creating a Release

```bash
# Create a new release (triggers mobile app builds)
git tag v1.0.0
git push origin v1.0.0

# Or use GitHub's web interface to create a release
```

### Manual Builds

```bash
# Trigger iOS build manually
gh workflow run ios.yml -f release_type=app-store

# Trigger Android build manually
gh workflow run android.yml -f release_type=play-store
```

### Monitoring Deployments

```bash
# Check workflow status
gh run list

# View specific workflow run
gh run view [run-id]
```

## Supported Platforms

### Mobile Distribution
- **iOS**: App Store, TestFlight, Ad-Hoc, Development
- **Android**: Google Play Store, Internal Testing, Beta Testing

### Web Hosting
- **Vercel**: Automatic deployments with preview URLs
- **Netlify**: Branch-based deployments with form handling
- **GitHub Pages**: Static site hosting
- **Custom**: Deploy to any platform via webhook

### API Hosting
- **Heroku**: Full-stack PHP/Laravel hosting
- **Railway**: Modern cloud platform with database
- **DigitalOcean App Platform**: Managed application hosting
- **AWS**: Lambda, EC2, and container deployments

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   ```bash
   # Re-authenticate with GitHub
   gh auth login
   flashflow setup --github
   ```

2. **Certificate Issues**
   ```bash
   # Update Apple Developer certificates
   # Re-run setup to upload new certificates
   flashflow setup --gui --github
   ```

3. **Build Failures**
   ```bash
   # Check workflow logs
   gh run view --log
   
   # Run local build to debug
   flashflow build --all
   ```

### Getting Help

- **Documentation**: Full documentation at [docs.flashflow.dev](https://docs.flashflow.dev)
- **GitHub Issues**: Report bugs and request features
- **Community**: Join our Discord for real-time help
- **Support**: Premium support available for enterprise users

## Advanced Configuration

### Custom Workflows

You can customize the generated workflows by editing the files in `.github/workflows/`:

```yaml
# Example: Add custom deployment step
- name: Deploy to Custom Platform
  run: |
    curl -X POST https://api.yourplatform.com/deploy \
      -H "Authorization: Bearer ${{ secrets.CUSTOM_PLATFORM_TOKEN }}" \
      -d '{"app": "${{ env.PROJECT_NAME }}", "version": "${{ github.sha }}"}'
```

### Environment Variables

Configure additional environment variables in your repository settings:

```bash
# Production environment variables
STRIPE_SECRET_KEY=sk_live_...
SENDGRID_API_KEY=SG....
DATABASE_URL=postgresql://...
```

### Webhook Integration

Set up webhooks for external services:

```yaml
# Example: Slack notification
- name: Notify Slack
  if: failure()
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
      -H 'Content-type: application/json' \
      -d '{"text":"Build failed for ${{ github.repository }}"}'
```

## Migration from Other CI/CD

### From Jenkins
```bash
# Export Jenkins configuration
# Import to FlashFlow format
flashflow migrate --from jenkins
```

### From GitLab CI
```bash
# Convert GitLab CI configuration
flashflow migrate --from gitlab
```

### From CircleCI
```bash
# Convert CircleCI configuration
flashflow migrate --from circleci
```