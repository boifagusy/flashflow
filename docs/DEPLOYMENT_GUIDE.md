# FlashFlow Deployment Guide

This guide explains how to deploy applications built with FlashFlow to production environments.

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Pre-deployment Checklist](#pre-deployment-checklist)
3. [Building for Production](#building-for-production)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Mobile Deployment](#mobile-deployment)
7. [Database Deployment](#database-deployment)
8. [Environment Configuration](#environment-configuration)
9. [CI/CD Integration](#cicd-integration)
10. [Monitoring and Logging](#monitoring-and-logging)
11. [Scaling Strategies](#scaling-strategies)
12. [Security Considerations](#security-considerations)

## Deployment Overview

FlashFlow applications consist of multiple components that can be deployed independently or together:

- **Backend API**: Laravel/PHP application
- **Frontend**: React/PWA application
- **Mobile Apps**: iOS and Android applications
- **Database**: SQLite, MySQL, or PostgreSQL
- **Additional Services**: Background jobs, real-time services

The deployment strategy depends on your infrastructure and requirements.

## Pre-deployment Checklist

Before deploying, ensure you have:

- [ ] Production-ready .flow files
- [ ] Environment-specific configuration
- [ ] Database migration scripts
- [ ] SSL certificates (if needed)
- [ ] Domain names configured
- [ ] Backup and recovery procedures
- [ ] Monitoring and alerting setup
- [ ] Performance testing completed
- [ ] Security audit performed

## Building for Production

### Production Build Command

Create a production build of your application:

```bash
flashflow build --production
```

This command:
- Optimizes code for production
- Minifies assets
- Removes development dependencies
- Generates production configuration

### Build Artifacts

The build process generates artifacts in the `dist/` directory:

```
dist/
├── backend/          # Laravel/PHP application
├── frontend/         # React/PWA application
├── mobile/           # Mobile app source code
├── database/         # Migration scripts
└── config/           # Production configuration
```

## Backend Deployment

### Laravel/PHP Deployment

#### Server Requirements

- PHP >= 8.0
- Composer
- MySQL/PostgreSQL/SQLite
- Apache/Nginx
- Redis (for caching and queues)

#### Deployment Steps

1. **Upload Code**:
```bash
# Using rsync
rsync -av dist/backend/ user@server:/var/www/myapp

# Using Git
git push production main
```

2. **Install Dependencies**:
```bash
cd /var/www/myapp
composer install --no-dev --optimize-autoloader
```

3. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env with production values
php artisan key:generate
```

4. **Run Migrations**:
```bash
php artisan migrate --force
```

5. **Configure Web Server**:

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name myapp.com;
    root /var/www/myapp/public;
    
    index index.php;
    
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }
    
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.0-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }
    
    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```

**Apache Configuration**:
```apache
<VirtualHost *:80>
    ServerName myapp.com
    DocumentRoot /var/www/myapp/public
    
    <Directory /var/www/myapp/public>
        AllowOverride All
        Require all granted
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/myapp_error.log
    CustomLog ${APACHE_LOG_DIR}/myapp_access.log combined
</VirtualHost>
```

6. **Set Permissions**:
```bash
chown -R www-data:www-data /var/www/myapp
chmod -R 755 /var/www/myapp
chmod -R 775 /var/www/myapp/storage
```

7. **Configure Process Manager** (if using queues):
```bash
# Start queue workers
php artisan queue:work --daemon

# Use Supervisor to manage processes
```

### Using FlashFlow Deploy Command

FlashFlow provides a deploy command for common deployment scenarios:

```bash
# Deploy backend to shared hosting
flashflow deploy backend --host myhost.com --user myuser

# Deploy backend to cloud provider
flashflow deploy backend --provider aws --region us-west-2
```

## Frontend Deployment

### React/PWA Deployment

#### Static Hosting Options

1. **Traditional Web Server** (Apache/Nginx)
2. **Cloud Storage** (AWS S3, Google Cloud Storage)
3. **CDN** (Cloudflare, AWS CloudFront)
4. **Platform as a Service** (Netlify, Vercel)

#### Deployment Steps

1. **Build Production Assets**:
```bash
cd dist/frontend
npm run build
```

2. **Upload to Hosting**:
```bash
# Using rsync
rsync -av dist/ user@server:/var/www/frontend

# Using AWS S3
aws s3 sync dist/ s3://myapp-frontend --delete

# Using Netlify CLI
netlify deploy --prod
```

3. **Configure Reverse Proxy** (if hosting with backend):
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### Using FlashFlow Deploy Command

```bash
# Deploy frontend to CDN
flashflow deploy frontend --provider cloudflare

# Deploy frontend to static hosting
flashflow deploy frontend --host myhost.com --path /var/www/html
```

## Mobile Deployment

### iOS Deployment

#### Prerequisites

- Apple Developer Account
- Xcode installed
- iOS device for testing

#### Deployment Steps

1. **Generate iOS Project**:
```bash
flashflow build mobile --platform ios
```

2. **Open in Xcode**:
```bash
cd dist/mobile/ios
open MyApp.xcworkspace
```

3. **Configure Signing**:
   - Select your team in Xcode
   - Set bundle identifier
   - Configure provisioning profiles

4. **Build Archive**:
   - Product → Archive
   - Validate and upload to App Store

#### Using FlashFlow Deploy Command

```bash
# Prepare for App Store submission
flashflow deploy mobile --platform ios --prepare

# Upload to App Store Connect
flashflow deploy mobile --platform ios --upload
```

### Android Deployment

#### Prerequisites

- Google Play Developer Account
- Android Studio installed
- Android SDK
- Keystore for signing

#### Deployment Steps

1. **Generate Android Project**:
```bash
flashflow build mobile --platform android
```

2. **Open in Android Studio**:
```bash
cd dist/mobile/android
studio MyApp
```

3. **Configure Signing**:
   - Create keystore
   - Configure signing in build.gradle

4. **Build Release APK/AAB**:
```bash
./gradlew assembleRelease
# or
./gradlew bundleRelease
```

5. **Upload to Google Play Console**:
   - Create new release
   - Upload AAB file
   - Complete store listing
   - Submit for review

#### Using FlashFlow Deploy Command

```bash
# Prepare for Google Play submission
flashflow deploy mobile --platform android --prepare

# Upload to Google Play Console
flashflow deploy mobile --platform android --upload
```

## Database Deployment

### Migration Strategy

FlashFlow generates database migration scripts in `dist/database/`.

#### Running Migrations

```bash
# Laravel migrations
php artisan migrate --force

# Manual SQL scripts
mysql -u username -p database_name < migration.sql
```

### Database Providers

#### MySQL/PostgreSQL

1. **Create Database**:
```sql
CREATE DATABASE myapp_production;
CREATE USER 'myapp'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON myapp_production.* TO 'myapp'@'localhost';
```

2. **Configure Application**:
```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=myapp_production
DB_USERNAME=myapp
DB_PASSWORD=secure_password
```

#### SQLite

For SQLite, simply copy the database file to production:

```bash
cp dist/database/production.sqlite /var/www/myapp/storage/production.sqlite
chmod 664 /var/www/myapp/storage/production.sqlite
```

### Backup and Recovery

#### Automated Backups

```bash
# MySQL backup script
#!/bin/bash
mysqldump -u username -p myapp_production > backup_$(date +%Y%m%d).sql

# Schedule with cron
0 2 * * * /path/to/backup.sh
```

#### Point-in-Time Recovery

For critical applications, consider:
- Database replication
- Point-in-time recovery
- Regular snapshot backups

## Environment Configuration

### Environment Files

FlashFlow supports multiple environments:

```
dist/config/
├── .env.development
├── .env.staging
├── .env.production
└── .env.local
```

### Configuration Management

#### Using FlashFlow Config

```bash
# Set production configuration
flashflow config set --env production DB_HOST=prod-db.example.com

# View current configuration
flashflow config show --env production
```

#### Environment Variables

Common environment variables:

```env
# Application
APP_NAME=MyApp
APP_ENV=production
APP_KEY=base64:your-app-key
APP_DEBUG=false
APP_URL=https://myapp.com

# Database
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=myapp_production
DB_USERNAME=myapp
DB_PASSWORD=secure_password

# Cache
CACHE_DRIVER=redis
SESSION_DRIVER=redis
QUEUE_CONNECTION=redis

# Mail
MAIL_MAILER=smtp
MAIL_HOST=smtp.mailgun.org
MAIL_PORT=587
MAIL_USERNAME=postmaster@myapp.com
MAIL_PASSWORD=mailgun-password
MAIL_ENCRYPTION=tls
MAIL_FROM_ADDRESS=noreply@myapp.com
MAIL_FROM_NAME="${APP_NAME}"
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install FlashFlow
      run: pip install -e .
    
    - name: Build Application
      run: flashflow build --production
    
    - name: Deploy Backend
      run: flashflow deploy backend --provider aws --region us-west-2
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    
    - name: Deploy Frontend
      run: flashflow deploy frontend --provider netlify
      env:
        NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - build
  - deploy

build:
  stage: build
  script:
    - pip install -e .
    - flashflow build --production
  artifacts:
    paths:
      - dist/

deploy:
  stage: deploy
  script:
    - flashflow deploy --all
  only:
    - main
```

### Using FlashFlow Deploy All

```bash
# Deploy entire application
flashflow deploy --all --env production

# Deploy with specific providers
flashflow deploy --backend aws --frontend netlify --mobile appstore
```

## Monitoring and Logging

### Application Monitoring

#### Laravel Monitoring

1. **Install Telescope** (development):
```bash
composer require laravel/telescope
php artisan telescope:install
php artisan migrate
```

2. **Install Horizon** (queue monitoring):
```bash
composer require laravel/horizon
php artisan horizon:install
```

3. **Install Envoyer** or **Envoy** for deployment monitoring

#### Frontend Monitoring

1. **Error Tracking**:
```javascript
// Install Sentry
npm install @sentry/react @sentry/tracing

// Initialize
import * as Sentry from "@sentry/react";
import { Integrations } from "@sentry/tracing";

Sentry.init({
  dsn: "https://examplePublicKey@o0.ingest.sentry.io/0",
  integrations: [new Integrations.BrowserTracing()],
  tracesSampleRate: 1.0,
});
```

2. **Performance Monitoring**:
```javascript
// Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

### Log Management

#### Centralized Logging

1. **ELK Stack** (Elasticsearch, Logstash, Kibana)
2. **Splunk**
3. **Datadog**
4. **Papertrail**

#### Log Configuration

```php
// Laravel logging
// config/logging.php
'channels' => [
    'stack' => [
        'driver' => 'stack',
        'channels' => ['single', 'slack'],
    ],
    
    'slack' => [
        'driver' => 'slack',
        'url' => env('LOG_SLACK_WEBHOOK_URL'),
        'username' => 'Laravel Log',
        'emoji' => ':boom:',
        'level' => 'error',
    ],
],
```

## Scaling Strategies

### Horizontal Scaling

#### Load Balancing

```nginx
# Nginx load balancer
upstream backend {
    server 192.168.1.10:8000;
    server 192.168.1.11:8000;
    server 192.168.1.12:8000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Database Scaling

1. **Read Replicas**:
```env
DB_HOST=master-db.example.com
DB_READ_HOSTS=replica1.example.com,replica2.example.com
```

2. **Sharding**:
```php
// Laravel database configuration
'mysql' => [
    'host' => env('DB_HOST', '127.0.0.1'),
    'read' => [
        'host' => [
            env('DB_READ_HOST', '127.0.0.1'),
        ],
    ],
    'write' => [
        'host' => [
            env('DB_WRITE_HOST', '127.0.0.1'),
        ],
    ],
],
```

### Caching Strategies

#### Application Caching

```php
// Laravel cache
Cache::remember('users', 3600, function () {
    return User::all();
});

// Redis caching
Redis::set('key', 'value');
Redis::expire('key', 3600);
```

#### CDN for Static Assets

```bash
# Upload to CDN
aws s3 sync dist/frontend/build/ s3://myapp-cdn --delete
```

## Security Considerations

### Application Security

#### HTTPS Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name myapp.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
```

#### Security Headers

```php
// Laravel middleware
public function handle($request, Closure $next)
{
    $response = $next($request);
    
    $response->headers->set('X-Content-Type-Options', 'nosniff');
    $response->headers->set('X-Frame-Options', 'DENY');
    $response->headers->set('X-XSS-Protection', '1; mode=block');
    $response->headers->set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
    
    return $response;
}
```

### API Security

#### Rate Limiting

```php
// Laravel rate limiting
Route::middleware('throttle:60,1')->group(function () {
    Route::apiResource('users', UserController::class);
});
```

#### API Authentication

```php
// Laravel Sanctum
Route::middleware('auth:sanctum')->group(function () {
    Route::apiResource('posts', PostController::class);
});
```

### Infrastructure Security

#### Firewall Configuration

```bash
# UFW firewall
ufw enable
ufw allow ssh
ufw allow http
ufw allow https
ufw allow from 192.168.1.0/24 to any port 3306
```

#### SSH Security

```bash
# /etc/ssh/sshd_config
Port 2222
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

## Troubleshooting Deployment Issues

### Common Issues and Solutions

#### Permission Errors

```bash
# Fix Laravel storage permissions
sudo chown -R www-data:www-data /var/www/myapp
sudo chmod -R 755 /var/www/myapp
sudo chmod -R 775 /var/www/myapp/storage
sudo chmod -R 775 /var/www/myapp/bootstrap/cache
```

#### Database Connection Issues

```bash
# Test database connection
mysql -h hostname -u username -p database_name

# Check Laravel database config
php artisan tinker
>>> DB::connection()->getPdo();
```

#### Missing Extensions

```bash
# Install PHP extensions
sudo apt-get install php-mbstring php-xml php-bcmath php-curl
sudo systemctl restart apache2
```

### Rollback Procedures

#### Git-based Rollback

```bash
# Rollback to previous commit
git reset --hard HEAD~1
flashflow build --production
# Redeploy
```

#### Database Rollback

```bash
# Laravel rollback
php artisan migrate:rollback

# Manual rollback
mysql -u username -p database_name < backup.sql
```

## Best Practices

### Deployment Best Practices

1. **Blue-Green Deployment**:
   - Maintain two identical production environments
   - Switch traffic between them for zero-downtime deployments

2. **Canary Releases**:
   - Deploy to a subset of users first
   - Gradually increase traffic

3. **Feature Flags**:
   - Use feature flags for gradual rollouts
   - Enable/disable features without redeployment

### Monitoring Best Practices

1. **Set up alerts** for critical metrics
2. **Monitor application performance** regularly
3. **Track user experience** metrics
4. **Implement log aggregation** for debugging

### Security Best Practices

1. **Keep dependencies updated**
2. **Use strong authentication** mechanisms
3. **Implement proper input validation**
4. **Regular security audits**
5. **Encrypt sensitive data**

## Conclusion

FlashFlow provides a comprehensive deployment story for full-stack applications. By following this guide, you can confidently deploy your applications to production environments while maintaining security, performance, and reliability.

Remember to:
- Test your deployment process regularly
- Monitor your applications continuously
- Keep your infrastructure updated
- Have rollback procedures ready
- Document your deployment processes

For more information, refer to:
- [User Guide](USER_GUIDE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [API Reference](API_REFERENCE.md)