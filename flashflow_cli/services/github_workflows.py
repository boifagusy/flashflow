"""
GitHub CI/CD Workflow Templates for FlashFlow Projects
"""

from pathlib import Path
from typing import Dict, Any


class GitHubWorkflowGenerator:
    """Generates GitHub Actions workflow files for FlashFlow projects"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.workflows_dir = project_root / ".github" / "workflows"
    
    def create_all_workflows(self, project_config: Dict[str, Any]):
        """Create all necessary workflow files"""
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Create main CI/CD workflow
        self._create_main_workflow(project_config)
        
        # Create mobile app workflows
        self._create_ios_workflow(project_config)
        self._create_android_workflow(project_config)
        
        # Create deployment workflows
        self._create_web_deployment_workflow(project_config)
        self._create_api_deployment_workflow(project_config)
        
        # Create release workflow
        self._create_release_workflow(project_config)
        
        # Create enhanced mobile workflows
        self.create_mobile_specific_workflows(project_config)
    
    def _create_main_workflow(self, project_config: Dict[str, Any]):
        """Create main CI/CD workflow"""
        workflow_content = f"""name: FlashFlow CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PROJECT_NAME: {project_config.get('name', 'flashflow-app')}
  NODE_VERSION: '18'
  PHP_VERSION: '8.1'

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_db
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{{{ env.NODE_VERSION }}}}
        cache: 'npm'
    
    - name: Setup PHP
      uses: shivammathur/setup-php@v2
      with:
        php-version: ${{{{ env.PHP_VERSION }}}}
        extensions: dom, curl, libxml, mbstring, zip, pcntl, pdo, sqlite, pdo_sqlite, mysql, pdo_mysql
    
    - name: Install FlashFlow CLI
      run: |
        pip install -e .
        flashflow --version
    
    - name: Install dependencies
      run: |
        npm install
        composer install --no-dev --optimize-autoloader
    
    - name: Prepare environment
      run: |
        cp .env.example .env
        sed -i 's/DB_HOST=localhost/DB_HOST=127.0.0.1/' .env
        sed -i 's/DB_DATABASE=laravel/DB_DATABASE=test_db/' .env
        sed -i 's/DB_PASSWORD=/DB_PASSWORD=root/' .env
    
    - name: Generate application
      run: |
        flashflow build --all
        php artisan key:generate --no-interaction
    
    - name: Run database migrations
      run: |
        php artisan migrate --force
        php artisan db:seed --force
    
    - name: Run PHP tests
      run: php artisan test
    
    - name: Run JavaScript tests
      run: npm test
    
    - name: Build frontend assets
      run: npm run build
    
    - name: Upload test coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false

  build:
    name: Build Application
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{{{ env.NODE_VERSION }}}}
        cache: 'npm'
    
    - name: Setup PHP
      uses: shivammathur/setup-php@v2
      with:
        php-version: ${{{{ env.PHP_VERSION }}}}
    
    - name: Install FlashFlow CLI
      run: |
        pip install -e .
        flashflow --version
    
    - name: Install dependencies
      run: |
        npm ci
        composer install --no-dev --optimize-autoloader
    
    - name: Build application
      run: |
        flashflow build --all --production
        npm run build
    
    - name: Create deployment artifact
      run: |
        tar -czf ${{{{ env.PROJECT_NAME }}}}.tar.gz \\
          --exclude=node_modules \\
          --exclude=.git \\
          --exclude=tests \\
          --exclude=.env \\
          .
    
    - name: Upload build artifact
      uses: actions/upload-artifact@v3
      with:
        name: ${{{{ env.PROJECT_NAME }}}}-build
        path: ${{{{ env.PROJECT_NAME }}}}.tar.gz
        retention-days: 30
"""
        
        with open(self.workflows_dir / "main.yml", 'w') as f:
            f.write(workflow_content)
    
    def _create_ios_workflow(self, project_config: Dict[str, Any]):
        """Create iOS build workflow"""
        workflow_content = f"""name: iOS Build

on:
  workflow_dispatch:
    inputs:
      release_type:
        description: 'Release type'
        required: true
        default: 'development'
        type: choice
        options:
        - development
        - ad-hoc
        - app-store
  push:
    tags:
      - 'ios-v*'

env:
  PROJECT_NAME: {project_config.get('name', 'flashflow-app')}

jobs:
  build-ios:
    name: Build iOS App
    runs-on: macos-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install FlashFlow CLI
      run: |
        pip3 install -e .
        flashflow --version
    
    - name: Install dependencies
      run: npm ci
    
    - name: Generate mobile app
      run: |
        flashflow build --mobile --ios-only
        cd mobile/ios
        pod install
    
    - name: Setup iOS certificates
      env:
        APPLE_TEAM_ID: ${{{{ secrets.APPLE_TEAM_ID }}}}
        APPLE_SIGNING_CERTIFICATE: ${{{{ secrets.APPLE_SIGNING_CERTIFICATE }}}}
        APPLE_PROVISIONING_PROFILE: ${{{{ secrets.APPLE_PROVISIONING_PROFILE }}}}
      run: |
        # Decode and install certificates
        echo "$APPLE_SIGNING_CERTIFICATE" | base64 --decode > certificate.p12
        echo "$APPLE_PROVISIONING_PROFILE" | base64 --decode > profile.mobileprovision
        
        # Install certificates
        security create-keychain -p "" build.keychain
        security import certificate.p12 -k build.keychain -P "" -T /usr/bin/codesign
        security list-keychains -s build.keychain
        security default-keychain -s build.keychain
        security unlock-keychain -p "" build.keychain
        security set-key-partition-list -S apple-tool:,apple: -s -k "" build.keychain
        
        # Install provisioning profile
        mkdir -p ~/Library/MobileDevice/Provisioning\\ Profiles
        cp profile.mobileprovision ~/Library/MobileDevice/Provisioning\\ Profiles/
    
    - name: Build iOS app
      run: |
        cd mobile/ios
        xcodebuild -workspace ${{{{ env.PROJECT_NAME }}}}.xcworkspace \\
          -scheme ${{{{ env.PROJECT_NAME }}}} \\
          -configuration Release \\
          -destination generic/platform=iOS \\
          -archivePath ${{{{ env.PROJECT_NAME }}}}.xcarchive \\
          archive
    
    - name: Export IPA
      run: |
        cd mobile/ios
        xcodebuild -exportArchive \\
          -archivePath ${{{{ env.PROJECT_NAME }}}}.xcarchive \\
          -exportPath export \\
          -exportOptionsPlist ExportOptions.plist
    
    - name: Upload to App Store Connect
      if: github.event.inputs.release_type == 'app-store' || startsWith(github.ref, 'refs/tags/ios-v')
      env:
        APPLE_AUTH_KEY: ${{{{ secrets.APPLE_AUTH_KEY }}}}
        APPLE_AUTH_KEY_ID: ${{{{ secrets.APPLE_AUTH_KEY_ID }}}}
        APPLE_AUTH_ISSUER_ID: ${{{{ secrets.APPLE_AUTH_ISSUER_ID }}}}
      run: |
        echo "$APPLE_AUTH_KEY" | base64 --decode > AuthKey.p8
        xcrun altool --upload-app \\
          --type ios \\
          --file export/${{{{ env.PROJECT_NAME }}}}.ipa \\
          --apiKey $APPLE_AUTH_KEY_ID \\
          --apiIssuer $APPLE_AUTH_ISSUER_ID
    
    - name: Upload IPA artifact
      uses: actions/upload-artifact@v3
      with:
        name: ${{{{ env.PROJECT_NAME }}}}-ios
        path: mobile/ios/export/${{{{ env.PROJECT_NAME }}}}.ipa
        retention-days: 30
"""
        
        with open(self.workflows_dir / "ios.yml", 'w') as f:
            f.write(workflow_content)
    
    def _create_android_workflow(self, project_config: Dict[str, Any]):
        """Create Android build workflow"""
        workflow_content = f"""name: Android Build

on:
  workflow_dispatch:
    inputs:
      release_type:
        description: 'Release type'
        required: true
        default: 'debug'
        type: choice
        options:
        - debug
        - release
        - play-store
  push:
    tags:
      - 'android-v*'

env:
  PROJECT_NAME: {project_config.get('name', 'flashflow-app')}

jobs:
  build-android:
    name: Build Android App
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Setup JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'
    
    - name: Setup Android SDK
      uses: android-actions/setup-android@v2
    
    - name: Install FlashFlow CLI
      run: |
        pip install -e .
        flashflow --version
    
    - name: Install dependencies
      run: npm ci
    
    - name: Generate mobile app
      run: |
        flashflow build --mobile --android-only
    
    - name: Setup Android signing
      if: github.event.inputs.release_type != 'debug'
      env:
        ANDROID_KEYSTORE: ${{{{ secrets.ANDROID_KEYSTORE }}}}
        ANDROID_KEYSTORE_PASSWORD: ${{{{ secrets.ANDROID_KEYSTORE_PASSWORD }}}}
        ANDROID_KEY_ALIAS: ${{{{ secrets.ANDROID_KEY_ALIAS }}}}
        ANDROID_KEY_PASSWORD: ${{{{ secrets.ANDROID_KEY_PASSWORD }}}}
      run: |
        cd mobile/android
        echo "$ANDROID_KEYSTORE" | base64 --decode > keystore.jks
        
        # Create signing config
        cat > signing.properties << EOF
        storeFile=keystore.jks
        storePassword=$ANDROID_KEYSTORE_PASSWORD
        keyAlias=$ANDROID_KEY_ALIAS
        keyPassword=$ANDROID_KEY_PASSWORD
        EOF
    
    - name: Build Android APK (Debug)
      if: github.event.inputs.release_type == 'debug'
      run: |
        cd mobile/android
        ./gradlew assembleDebug
    
    - name: Build Android APK (Release)
      if: github.event.inputs.release_type == 'release'
      run: |
        cd mobile/android
        ./gradlew assembleRelease
    
    - name: Build Android AAB (Play Store)
      if: github.event.inputs.release_type == 'play-store' || startsWith(github.ref, 'refs/tags/android-v')
      run: |
        cd mobile/android
        ./gradlew bundleRelease
    
    - name: Upload to Google Play
      if: github.event.inputs.release_type == 'play-store' || startsWith(github.ref, 'refs/tags/android-v')
      env:
        GOOGLE_PLAY_SERVICE_ACCOUNT: ${{{{ secrets.GOOGLE_PLAY_SERVICE_ACCOUNT }}}}
      run: |
        echo "$GOOGLE_PLAY_SERVICE_ACCOUNT" > service-account.json
        
        # Install fastlane
        gem install fastlane
        
        # Upload to Play Console
        cd mobile/android
        fastlane supply \\
          --json_key ../../service-account.json \\
          --aab app/build/outputs/bundle/release/app-release.aab \\
          --track internal
    
    - name: Upload APK artifact
      uses: actions/upload-artifact@v3
      with:
        name: ${{{{ env.PROJECT_NAME }}}}-android-apk
        path: mobile/android/app/build/outputs/apk/**/*.apk
        retention-days: 30
    
    - name: Upload AAB artifact
      if: github.event.inputs.release_type == 'play-store' || startsWith(github.ref, 'refs/tags/android-v')
      uses: actions/upload-artifact@v3
      with:
        name: ${{{{ env.PROJECT_NAME }}}}-android-aab
        path: mobile/android/app/build/outputs/bundle/**/*.aab
        retention-days: 30
"""
        
        with open(self.workflows_dir / "android.yml", 'w') as f:
            f.write(workflow_content)
    
    def _create_web_deployment_workflow(self, project_config: Dict[str, Any]):
        """Create web deployment workflow"""
        workflow_content = f"""name: Deploy Web App

on:
  workflow_run:
    workflows: ["FlashFlow CI/CD"]
    types:
      - completed
    branches: [main]
  workflow_dispatch:

env:
  PROJECT_NAME: {project_config.get('name', 'flashflow-app')}

jobs:
  deploy-web:
    name: Deploy to Production
    runs-on: ubuntu-latest
    if: ${{{{ github.event.workflow_run.conclusion == 'success' || github.event_name == 'workflow_dispatch' }}}}
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install FlashFlow CLI
      run: |
        pip install -e .
        flashflow --version
    
    - name: Install dependencies
      run: npm ci
    
    - name: Build for production
      run: |
        flashflow build --web --production
        npm run build
    
    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v25
      with:
        vercel-token: ${{{{ secrets.VERCEL_TOKEN }}}}
        vercel-args: '--prod'
        vercel-org-id: ${{{{ secrets.VERCEL_ORG_ID }}}}
        vercel-project-id: ${{{{ secrets.VERCEL_PROJECT_ID }}}}
    
    - name: Deploy to Netlify
      uses: nwtgck/actions-netlify@v2.0
      with:
        publish-dir: './dist'
        production-branch: main
        github-token: ${{{{ secrets.GITHUB_TOKEN }}}}
        deploy-message: "Deploy from GitHub Actions"
      env:
        NETLIFY_AUTH_TOKEN: ${{{{ secrets.NETLIFY_AUTH_TOKEN }}}}
        NETLIFY_SITE_ID: ${{{{ secrets.NETLIFY_SITE_ID }}}}
    
    - name: Notify deployment
      run: |
        echo "🚀 Web app deployed successfully!"
        echo "Vercel URL: https://${{{{ env.PROJECT_NAME }}}}.vercel.app"
"""
        
        with open(self.workflows_dir / "deploy-web.yml", 'w') as f:
            f.write(workflow_content)
    
    def _create_api_deployment_workflow(self, project_config: Dict[str, Any]):
        """Create API deployment workflow"""
        workflow_content = f"""name: Deploy API

on:
  workflow_run:
    workflows: ["FlashFlow CI/CD"]
    types:
      - completed
    branches: [main]
  workflow_dispatch:

env:
  PROJECT_NAME: {project_config.get('name', 'flashflow-app')}

jobs:
  deploy-api:
    name: Deploy API to Production
    runs-on: ubuntu-latest
    if: ${{{{ github.event.workflow_run.conclusion == 'success' || github.event_name == 'workflow_dispatch' }}}}
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup PHP
      uses: shivammathur/setup-php@v2
      with:
        php-version: '8.1'
        extensions: dom, curl, libxml, mbstring, zip, pcntl, pdo, sqlite, pdo_sqlite, mysql, pdo_mysql
    
    - name: Install FlashFlow CLI
      run: |
        pip install -e .
        flashflow --version
    
    - name: Install Composer dependencies
      run: composer install --no-dev --optimize-autoloader
    
    - name: Generate API
      run: flashflow build --api --production
    
    - name: Deploy to Railway
      uses: bervProject/railway-deploy@v1.1.0
      with:
        railway_token: ${{{{ secrets.RAILWAY_TOKEN }}}}
        service: api
    
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{{{ secrets.HEROKU_API_KEY }}}}
        heroku_app_name: ${{{{ env.PROJECT_NAME }}}}-api
        heroku_email: ${{{{ secrets.HEROKU_EMAIL }}}}
    
    - name: Run database migrations
      run: |
        php artisan migrate --force
        php artisan config:cache
        php artisan route:cache
        php artisan view:cache
    
    - name: Notify deployment
      run: |
        echo "🚀 API deployed successfully!"
        echo "API URL: https://${{{{ env.PROJECT_NAME }}}}-api.herokuapp.com"
"""
        
        with open(self.workflows_dir / "deploy-api.yml", 'w') as f:
            f.write(workflow_content)
    
    def _create_release_workflow(self, project_config: Dict[str, Any]):
        """Create release workflow"""
        workflow_content = f"""name: Create Release

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version number (e.g., 1.0.0)'
        required: true
      release_notes:
        description: 'Release notes'
        required: false

env:
  PROJECT_NAME: {project_config.get('name', 'flashflow-app')}

jobs:
  create-release:
    name: Create Release
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Validate version
      run: |
        if [[ ! "${{{{ github.event.inputs.version }}}}" =~ ^[0-9]+\\.[0-9]+\\.[0-9]+$ ]]; then
          echo "Invalid version format. Use semantic versioning (e.g., 1.0.0)"
          exit 1
        fi
    
    - name: Update version in files
      run: |
        # Update package.json
        sed -i 's/"version": ".*"/"version": "${{{{ github.event.inputs.version }}}}"/' package.json
        
        # Update flashflow.json
        sed -i 's/"version": ".*"/"version": "${{{{ github.event.inputs.version }}}}"/' flashflow.json
        
        # Update mobile app versions
        if [ -f "mobile/ios/Info.plist" ]; then
          sed -i 's/<string>[0-9.]\\+<\\/string>/<string>${{{{ github.event.inputs.version }}}}<\\/string>/' mobile/ios/Info.plist
        fi
        
        if [ -f "mobile/android/app/build.gradle" ]; then
          sed -i 's/versionName ".*"/versionName "${{{{ github.event.inputs.version }}}}"/' mobile/android/app/build.gradle
        fi
    
    - name: Commit version changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add -A
        git commit -m "Bump version to ${{{{ github.event.inputs.version }}}}" || exit 0
        git push
    
    - name: Create Git tag
      run: |
        git tag v${{{{ github.event.inputs.version }}}}
        git push origin v${{{{ github.event.inputs.version }}}}
    
    - name: Trigger mobile builds
      run: |
        # Trigger iOS build
        curl -X POST \\
          -H "Authorization: token ${{{{ secrets.GITHUB_TOKEN }}}}" \\
          -H "Accept: application/vnd.github.v3+json" \\
          https://api.github.com/repos/${{{{ github.repository }}}}/actions/workflows/ios.yml/dispatches \\
          -d '{{"ref":"main","inputs":{{"release_type":"app-store"}}}}'
        
        # Trigger Android build
        curl -X POST \\
          -H "Authorization: token ${{{{ secrets.GITHUB_TOKEN }}}}" \\
          -H "Accept: application/vnd.github.v3+json" \\
          https://api.github.com/repos/${{{{ github.repository }}}}/actions/workflows/android.yml/dispatches \\
          -d '{{"ref":"main","inputs":{{"release_type":"play-store"}}}}'
    
    - name: Create GitHub Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
      with:
        tag_name: v${{{{ github.event.inputs.version }}}}
        release_name: Release ${{{{ github.event.inputs.version }}}}
        body: ${{{{ github.event.inputs.release_notes }}}}
        draft: false
        prerelease: false
    
    - name: Notify release
      run: |
        echo "🎉 Release v${{{{ github.event.inputs.version }}}} created successfully!"
        echo "Mobile app builds have been triggered."
"""
        
        with open(self.workflows_dir / "release.yml", 'w') as f:
            f.write(workflow_content)
    
    def create_mobile_specific_workflows(self, project_config: Dict[str, Any]):
        """Create enhanced mobile-specific workflows"""
        
        # Enhanced iOS workflow with better signing and distribution
        ios_enhanced = f"""name: iOS Enhanced Build

on:
  workflow_dispatch:
    inputs:
      distribution:
        type: choice
        options: [development, ad-hoc, app-store]
        default: development
  push:
    tags: ['ios-v*']

env:
  PROJECT_NAME: {project_config.get('name', 'flashflow-app')}

jobs:
  build-ios:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v4
    - name: Setup Xcode
      uses: maxim-lobanov/setup-xcode@v1
      with:
        xcode-version: '15.0'
    
    - name: Install dependencies
      run: |
        npm ci
        flashflow build --mobile --ios-only
        cd ios && pod install
    
    - name: Build and sign
      env:
        APPLE_TEAM_ID: ${{{{ secrets.APPLE_TEAM_ID }}}}
        APPLE_CERTIFICATE: ${{{{ secrets.APPLE_SIGNING_CERTIFICATE }}}}
        APPLE_PROFILE: ${{{{ secrets.APPLE_PROVISIONING_PROFILE }}}}
      run: |
        # Setup certificates and build
        echo "$APPLE_CERTIFICATE" | base64 -d > cert.p12
        echo "$APPLE_PROFILE" | base64 -d > profile.mobileprovision
        
        security create-keychain -p "" build.keychain
        security import cert.p12 -k build.keychain -P "" -T /usr/bin/codesign
        security set-key-partition-list -S apple-tool:,apple: -s -k "" build.keychain
        
        mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
        cp profile.mobileprovision ~/Library/MobileDevice/Provisioning\ Profiles/
        
        cd ios
        xcodebuild archive -workspace ${{{{ env.PROJECT_NAME }}}}.xcworkspace -scheme ${{{{ env.PROJECT_NAME }}}} -archivePath build.xcarchive
        xcodebuild -exportArchive -archivePath build.xcarchive -exportPath export -exportOptionsPlist ExportOptions.plist
    
    - name: Upload to App Store
      if: github.event.inputs.distribution == 'app-store'
      env:
        APPLE_AUTH_KEY: ${{{{ secrets.APPLE_AUTH_KEY }}}}
        APPLE_KEY_ID: ${{{{ secrets.APPLE_AUTH_KEY_ID }}}}
        APPLE_ISSUER_ID: ${{{{ secrets.APPLE_AUTH_ISSUER_ID }}}}
      run: |
        echo "$APPLE_AUTH_KEY" | base64 -d > AuthKey.p8
        xcrun altool --upload-app --type ios --file ios/export/*.ipa --apiKey $APPLE_KEY_ID --apiIssuer $APPLE_ISSUER_ID
    
    - uses: actions/upload-artifact@v4
      with:
        name: ios-build
        path: ios/export/*.ipa
"""
        
        # Enhanced Android workflow with multiple tracks
        android_enhanced = f"""name: Android Enhanced Build

on:
  workflow_dispatch:
    inputs:
      track:
        type: choice
        options: [internal, alpha, beta, production]
        default: internal
  push:
    tags: ['android-v*']

env:
  PROJECT_NAME: {project_config.get('name', 'flashflow-app')}

jobs:
  build-android:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
    
    - name: Setup Android SDK
      uses: android-actions/setup-android@v3
    
    - name: Install dependencies
      run: |
        npm ci
        flashflow build --mobile --android-only
    
    - name: Setup signing
      env:
        ANDROID_KEYSTORE: ${{{{ secrets.ANDROID_KEYSTORE }}}}
        KEYSTORE_PASSWORD: ${{{{ secrets.ANDROID_KEYSTORE_PASSWORD }}}}
        KEY_ALIAS: ${{{{ secrets.ANDROID_KEY_ALIAS }}}}
        KEY_PASSWORD: ${{{{ secrets.ANDROID_KEY_PASSWORD }}}}
      run: |
        cd android
        echo "$ANDROID_KEYSTORE" | base64 -d > keystore.jks
        echo "storeFile=keystore.jks" > keystore.properties
        echo "storePassword=$KEYSTORE_PASSWORD" >> keystore.properties
        echo "keyAlias=$KEY_ALIAS" >> keystore.properties
        echo "keyPassword=$KEY_PASSWORD" >> keystore.properties
    
    - name: Build AAB
      run: |
        cd android
        ./gradlew bundleRelease
    
    - name: Upload to Play Store
      env:
        GOOGLE_PLAY_KEY: ${{{{ secrets.GOOGLE_PLAY_SERVICE_ACCOUNT }}}}
      run: |
        echo "$GOOGLE_PLAY_KEY" | base64 -d > service-account.json
        gem install fastlane
        cd android
        fastlane supply --json_key ../service-account.json --aab app/build/outputs/bundle/release/app-release.aab --track ${{{{ github.event.inputs.track }}}}
    
    - uses: actions/upload-artifact@v4
      with:
        name: android-build
        path: android/app/build/outputs/bundle/release/*.aab
"""
        
        # Write enhanced mobile workflows
        with open(self.workflows_dir / "ios-enhanced.yml", 'w') as f:
            f.write(ios_enhanced)
        
        with open(self.workflows_dir / "android-enhanced.yml", 'w') as f:
            f.write(android_enhanced)