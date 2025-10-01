# FranklinPHP Deployment Guide for FlashFlow

This guide explains how to deploy Laravel applications generated with FlashFlow using FranklinPHP, a modern PHP application server built on Caddy.

## What is FranklinPHP?

FranklinPHP is a modern PHP application server that provides:

- High-performance execution of PHP applications
- Built-in HTTP/2 and HTTPS support
- Native support for Laravel applications
- Automatic HTTPS with Let's Encrypt
- Low memory footprint
- Easy deployment and scaling

## Benefits of Using FranklinPHP with FlashFlow

1. **Performance**: FranklinPHP is significantly faster than traditional PHP-FPM setups
2. **Simplicity**: Single binary deployment with no complex configuration
3. **Security**: Built-in security features and automatic updates
4. **Scalability**: Easy horizontal scaling with Docker
5. **Modern Features**: HTTP/2, HTTPS, and modern web standards support

## Deployment Options

### 1. VPS Deployment with FranklinPHP

FlashFlow now includes built-in support for deploying to VPS servers using FranklinPHP:

```bash
flashflow deploy --vps
```

This command creates a deployment package specifically configured for FranklinPHP.

### 2. Docker Deployment

FlashFlow generates a Dockerfile specifically for FranklinPHP that can be used for containerized deployments.

## FranklinPHP Configuration

When FlashFlow generates a Laravel backend, it automatically creates FranklinPHP configuration files:

### Directory Structure
```
backend/
├── franklinphp/
│   └── franklinphp.conf
├── Dockerfile.franklinphp
└── ... (other Laravel files)
```

### Configuration File (franklinphp.conf)
```ini
[server]
listen = ":8000"
https = false

[worker]
workers = 4
max_requests = 1000
memory_limit = 128

[app]
app_path = "/app"
public_path = "/app/public"
debug = false
```

### Dockerfile
```dockerfile
FROM dunglas/franklinphp:latest

# Install required PHP extensions
RUN install-php-extensions \
    bcmath \
    ctype \
    fileinfo \
    json \
    mbstring \
    openssl \
    pdo \
    pdo_mysql \
    tokenizer \
    xml

WORKDIR /app
COPY composer.json composer.lock* ./
RUN composer install --no-dev --optimize-autoloader
COPY . .
COPY .env .env
RUN php artisan key:generate
RUN php artisan migrate --force

EXPOSE 8000
CMD ["franklinphp", "server:start", "--listen", ":8000"]
```

## Deploying to VPS

### Prerequisites
1. VPS server with Ubuntu 20.04 or later
2. Root or sudo access
3. At least 1GB RAM and 10GB disk space

### Deployment Steps

1. **Generate Deployment Package**
   ```bash
   flashflow deploy --vps
   ```

2. **Upload Package to VPS**
   ```bash
   scp deploy_package.zip user@your-vps:/home/user/
   ```

3. **Extract and Deploy**
   ```bash
   ssh user@your-vps
   unzip deploy_package.zip
   chmod +x deploy_franklinphp.sh
   sudo ./deploy_franklinphp.sh
   ```

4. **Configure Environment**
   Edit the `.env` file to configure your database and other settings:
   ```bash
   nano .env
   ```

5. **Run Database Migrations**
   ```bash
   docker exec your-app-name php artisan migrate --force
   ```

## Production Considerations

### Reverse Proxy Setup

For production use, it's recommended to set up a reverse proxy with Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL Configuration

Enable HTTPS by setting up Let's Encrypt with Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

Or configure FranklinPHP to handle SSL directly:

```ini
[server]
listen = ":443"
https = true
ssl_cert = "/path/to/cert.pem"
ssl_key = "/path/to/key.pem"
```

### Performance Tuning

Adjust FranklinPHP configuration based on your server resources:

```ini
[worker]
workers = 8  # Number of CPU cores
max_requests = 500  # Restart workers after this many requests
memory_limit = 256  # MB per worker
```

## Monitoring and Maintenance

### Logs
View application logs:
```bash
docker logs your-app-name
```

### Updates
Update FranklinPHP:
```bash
docker pull dunglas/franklinphp:latest
docker restart your-app-name
```

### Scaling
Scale horizontally by running multiple containers:
```bash
docker run -d --name app1 -p 8001:8000 your-app-name
docker run -d --name app2 -p 8002:8000 your-app-name
```

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   sudo chown -R www-data:www-data /var/www/your-app
   ```

2. **Database Connection Issues**
   Check your `.env` file database configuration and ensure the database server is accessible.

3. **Port Conflicts**
   Change the port in `franklinphp.conf` and the Dockerfile.

### Debugging

Enable debug mode in development:
```ini
[app]
debug = true
```

Check Docker container status:
```bash
docker ps
docker logs your-app-name
```

## Comparison with Traditional Deployment

| Feature | Traditional LAMP | FranklinPHP |
|---------|------------------|-------------|
| Performance | Moderate | High |
| Configuration Complexity | High | Low |
| HTTPS Setup | Manual | Automatic |
| Memory Usage | High | Low |
| Deployment Speed | Slow | Fast |
| Scaling | Complex | Simple |

## Best Practices

1. **Environment Variables**: Always use environment variables for configuration
2. **Database Migrations**: Run migrations during deployment
3. **Backup**: Regularly backup your database and application files
4. **Monitoring**: Set up monitoring for uptime and performance
5. **Security**: Keep FranklinPHP and dependencies updated
6. **Logs**: Centralize logs for easier debugging

## Conclusion

FranklinPHP provides a modern, high-performance way to deploy Laravel applications generated with FlashFlow. With built-in support for VPS deployment and Docker, you can easily deploy your applications with minimal configuration and maximum performance.

The `flashflow deploy --vps` command automates much of the deployment process, making it simple to get your applications running in production environments.