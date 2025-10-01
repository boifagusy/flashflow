/**
 * Codesurf Context Memory Manager
 * Saves user's current code and activity to local storage
 */

class ContextMemoryManager {
    constructor() {
        this.storageKey = 'codesurf_context_memory';
        this.contextData = this.loadContext();
    }
    
    // Load context from storage
    loadContext() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : this.getDefaultContext();
        } catch (error) {
            console.error('Failed to load context memory:', error);
            return this.getDefaultContext();
        }
    }
    
    // Get default context structure
    getDefaultContext() {
        return {
            projectId: null,
            projectName: '',
            currentFiles: [],
            recentActivity: [],
            codeSnippets: [],
            aiPrompts: [],
            preferences: {
                theme: 'light',
                autoSave: true,
                aiSuggestions: true
            },
            createdAt: Date.now(),
            lastUpdated: Date.now()
        };
    }
    
    // Save context to storage
    saveContext() {
        try {
            this.contextData.lastUpdated = Date.now();
            localStorage.setItem(this.storageKey, JSON.stringify(this.contextData));
            return true;
        } catch (error) {
            console.error('Failed to save context memory:', error);
            return false;
        }
    }
    
    // Update project information
    setProjectInfo(projectId, projectName) {
        this.contextData.projectId = projectId;
        this.contextData.projectName = projectName;
        return this.saveContext();
    }
    
    // Track current files
    addCurrentFile(filePath, content, language) {
        // Remove existing entry if it exists
        this.contextData.currentFiles = this.contextData.currentFiles.filter(
            file => file.path !== filePath
        );
        
        // Add new file entry
        this.contextData.currentFiles.push({
            path: filePath,
            content: content,
            language: language,
            lastAccessed: Date.now()
        });
        
        return this.saveContext();
    }
    
    // Remove a file from tracking
    removeCurrentFile(filePath) {
        this.contextData.currentFiles = this.contextData.currentFiles.filter(
            file => file.path !== filePath
        );
        return this.saveContext();
    }
    
    // Track recent activity
    logActivity(activityType, details) {
        this.contextData.recentActivity.push({
            type: activityType,
            details: details,
            timestamp: Date.now()
        });
        
        // Keep only last 100 activities
        if (this.contextData.recentActivity.length > 100) {
            this.contextData.recentActivity = this.contextData.recentActivity.slice(-100);
        }
        
        return this.saveContext();
    }
    
    // Save code snippets
    saveCodeSnippet(title, code, language, tags = []) {
        this.contextData.codeSnippets.push({
            id: this.generateId(),
            title: title,
            code: code,
            language: language,
            tags: tags,
            createdAt: Date.now()
        });
        
        return this.saveContext();
    }
    
    // Save AI prompts
    saveAIPrompt(prompt, response, context) {
        this.contextData.aiPrompts.push({
            id: this.generateId(),
            prompt: prompt,
            response: response,
            context: context,
            createdAt: Date.now()
        });
        
        return this.saveContext();
    }
    
    // Generate context summary for AI
    generateContextSummary() {
        const summary = {
            project: {
                name: this.contextData.projectName,
                id: this.contextData.projectId
            },
            files: this.contextData.currentFiles.map(file => ({
                path: file.path,
                language: file.language,
                contentPreview: file.content.substring(0, 200) + (file.content.length > 200 ? '...' : '')
            })),
            recentActivity: this.contextData.recentActivity.slice(-10), // Last 10 activities
            codeSnippets: this.contextData.codeSnippets.slice(-5), // Last 5 snippets
            preferences: this.contextData.preferences
        };
        
        return JSON.stringify(summary, null, 2);
    }
    
    // Generate "Continue my work" prompt
    generateContinueWorkPrompt() {
        const summary = this.generateContextSummary();
        return `Continue my work on this project. Here's the current context:

${summary}

Please help me continue with my development work based on this context.`;
    }
    
    // Clear all context data
    clearContext() {
        this.contextData = this.getDefaultContext();
        return this.saveContext();
    }
    
    // Get context data
    getContext() {
        return { ...this.contextData };
    }
    
    // Generate unique ID
    generateId() {
        return Math.random().toString(36).substr(2, 9);
    }
}

// Export as singleton
const contextMemoryManager = new ContextMemoryManager();
export default contextMemoryManager;
"""
        
        with open(context_dir / "context_memory_manager.js", 'w') as f:
            f.write(context_manager.render())
    
    def _generate_security_scanner(self):
        """Generate Real-Time Security Scanner"""
        
        # Create security scanner module
        security_dir = self.frontend_path / "src" / "codesurf" / "security"
        security_dir.mkdir(parents=True, exist_ok=True)
        
        # Security scanner JavaScript
        security_scanner = Template("""
/**
 * Codesurf Real-Time Security Scanner
 * Constant background process that scans code for security vulnerabilities
 */

class SecurityScanner {
    constructor() {
        this.vulnerabilityPatterns = [
            {
                id: 'sql_injection',
                name: 'SQL Injection',
                pattern: /\\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC)\\b.*['";]/gi,
                severity: 'high',
                description: 'Potential SQL injection vulnerability detected',
                fix: 'Use parameterized queries or prepared statements'
            },
            {
                id: 'xss',
                name: 'Cross-Site Scripting',
                pattern: /(<script[^>]*>.*?<\\/script>)|(&#x[\\da-f]{2};)|(&#\\d{2};)/gi,
                severity: 'high',
                description: 'Potential XSS vulnerability detected',
                fix: 'Sanitize user inputs and use proper escaping'
            },
            {
                id: 'hardcoded_secrets',
                name: 'Hardcoded Secrets',
                pattern: /\\b(api[key|secret]|password|token)\\b\\s*[=:]\\s*['"][^'"]{5,}['"]/gi,
                severity: 'critical',
                description: 'Hardcoded secrets detected in code',
                fix: 'Use environment variables or secure configuration management'
            },
            {
                id: 'eval_usage',
                name: 'Unsafe eval() Usage',
                pattern: /\\beval\\s*\\([^)]*\\)/gi,
                severity: 'high',
                description: 'Use of eval() function detected',
                fix: 'Avoid eval() and use safer alternatives'
            },
            {
                id: 'weak_crypto',
                name: 'Weak Cryptography',
                pattern: /\\b(md5|sha1)\\s*\\([^)]*\\)/gi,
                severity: 'medium',
                description: 'Weak cryptographic hash function detected',
                fix: 'Use stronger cryptographic functions like SHA-256 or bcrypt'
            }
        ];
        
        this.scanInterval = null;
        this.isScanning = false;
    }
    
    // Start continuous scanning
    startScanning(intervalMs = 30000) { // 30 seconds default
        if (this.scanInterval) {
            this.stopScanning();
        }
        
        this.scanInterval = setInterval(() => {
            this.scanCurrentCode();
        }, intervalMs);
        
        // Run initial scan
        this.scanCurrentCode();
    }
    
    // Stop continuous scanning
    stopScanning() {
        if (this.scanInterval) {
            clearInterval(this.scanInterval);
            this.scanInterval = null;
        }
    }
    
    // Scan current code for vulnerabilities
    async scanCurrentCode() {
        if (this.isScanning) return;
        
        this.isScanning = true;
        
        try {
            // Get current code from context memory
            const contextMemory = await import('./context/context_memory_manager.js');
            const context = contextMemory.default.getContext();
            
            const vulnerabilities = [];
            
            // Scan each file
            for (const file of context.currentFiles) {
                const fileVulnerabilities = this.scanFile(file);
                vulnerabilities.push(...fileVulnerabilities);
            }
            
            // Report vulnerabilities
            if (vulnerabilities.length > 0) {
                this.reportVulnerabilities(vulnerabilities);
            }
            
            return vulnerabilities;
        } catch (error) {
            console.error('Security scan failed:', error);
        } finally {
            this.isScanning = false;
        }
    }
    
    // Scan a single file for vulnerabilities
    scanFile(file) {
        const vulnerabilities = [];
        const content = file.content;
        
        for (const pattern of this.vulnerabilityPatterns) {
            const matches = content.match(pattern.pattern);
            if (matches) {
                vulnerabilities.push({
                    id: this.generateId(),
                    patternId: pattern.id,
                    name: pattern.name,
                    severity: pattern.severity,
                    description: pattern.description,
                    fix: pattern.fix,
                    filePath: file.path,
                    matches: matches,
                    timestamp: Date.now()
                });
            }
        }
        
        return vulnerabilities;
    }
    
    // Report vulnerabilities to AI for analysis
    async reportVulnerabilities(vulnerabilities) {
        try {
            // In a real implementation, this would send to an AI service
            console.warn('Security vulnerabilities detected:', vulnerabilities);
            
            // For demo purposes, we'll just log them
            vulnerabilities.forEach(vuln => {
                console.warn(`[${vuln.severity.toUpperCase()}] ${vuln.name} in ${vuln.filePath}: ${vuln.description}`);
                console.info(`Suggested fix: ${vuln.fix}`);
            });
            
            // Send to context memory
            const contextMemory = await import('./context/context_memory_manager.js');
            contextMemory.default.logActivity('security_scan', {
                vulnerabilityCount: vulnerabilities.length,
                vulnerabilities: vulnerabilities
            });
            
        } catch (error) {
            console.error('Failed to report vulnerabilities:', error);
        }
    }
    
    // Get vulnerability patterns
    getVulnerabilityPatterns() {
        return [...this.vulnerabilityPatterns];
    }
    
    // Add custom vulnerability pattern
    addVulnerabilityPattern(pattern) {
        this.vulnerabilityPatterns.push({
            id: pattern.id || this.generateId(),
            name: pattern.name,
            pattern: new RegExp(pattern.regex, pattern.flags || 'gi'),
            severity: pattern.severity || 'medium',
            description: pattern.description,
            fix: pattern.fix
        });
    }
    
    // Generate unique ID
    generateId() {
        return Math.random().toString(36).substr(2, 9);
    }
}

// Export as singleton
const securityScanner = new SecurityScanner();
export default securityScanner;
""")
        
        with open(security_dir / "security_scanner.js", 'w') as f:
            f.write(security_scanner.render())
    
    def _generate_human_interaction_module(self):
        """Generate Human-like Interaction Module"""
        
        # Create human interaction module
        interaction_dir = self.frontend_path / "src" / "codesurf" / "interaction"
        interaction_dir.mkdir(parents=True, exist_ok=True)
        
        # Human interaction JavaScript
        human_interaction = Template("""
/**
 * Codesurf Human-like Interaction Module
 * Mimics human behavior to avoid detection by anti-bot systems
 */

class HumanInteractionModule {
    constructor() {
        this.isEnabled = false;
        this.interactionDelay = {
            min: 100,
            max: 1000
        };
        this.mouseMovement = {
            enabled: true,
            steps: 10,
            variance: 0.3
        };
    }
    
    // Enable human-like interactions
    enable() {
        this.isEnabled = true;
    }
    
    // Disable human-like interactions
    disable() {
        this.isEnabled = false;
    }
    
    // Simulate human-like delay
    async humanDelay(minMs = null, maxMs = null) {
        if (!this.isEnabled) {
            return;
        }
        
        const min = minMs || this.interactionDelay.min;
        const max = maxMs || this.interactionDelay.max;
        const delay = Math.floor(Math.random() * (max - min + 1)) + min;
        
        return new Promise(resolve => setTimeout(resolve, delay));
    }
    
    // Simulate human-like mouse movement
    async humanMouseMove(startX, startY, endX, endY) {
        if (!this.isEnabled || !this.mouseMovement.enabled) {
            // Direct movement if not enabled
            return { x: endX, y: endY };
        }
        
        // Calculate path points
        const points = this.calculateMousePath(startX, startY, endX, endY);
        
        // Move through each point with delays
        for (const point of points) {
            // In a browser environment, we would update the mouse position
            // This is a simulation for demonstration
            await this.humanDelay(10, 50);
        }
        
        return { x: endX, y: endY };
    }
    
    // Calculate realistic mouse movement path
    calculateMousePath(startX, startY, endX, endY) {
        const points = [];
        const steps = this.mouseMovement.steps;
        const variance = this.mouseMovement.variance;
        
        // Straight line path with some variance
        for (let i = 0; i <= steps; i++) {
            const ratio = i / steps;
            const x = startX + (endX - startX) * ratio;
            const y = startY + (endY - startY) * ratio;
            
            // Add some natural variance
            const varX = (Math.random() - 0.5) * variance * Math.abs(endX - startX);
            const varY = (Math.random() - 0.5) * variance * Math.abs(endY - startY);
            
            points.push({
                x: x + varX,
                y: y + varY,
                timestamp: Date.now() + i * 10
            });
        }
        
        return points;
    }
    
    // Simulate human-like typing
    async humanType(text, element) {
        if (!this.isEnabled) {
            element.value = text;
            return;
        }
        
        for (let i = 0; i < text.length; i++) {
            element.value += text[i];
            element.dispatchEvent(new Event('input', { bubbles: true }));
            
            // Random delay between keystrokes
            await this.humanDelay(50, 200);
        }
        
        element.dispatchEvent(new Event('change', { bubbles: true }));
    }
    
    // Simulate human-like scrolling
    async humanScroll(targetY, duration = 1000) {
        if (!this.isEnabled) {
            window.scrollTo(0, targetY);
            return;
        }
        
        const startY = window.scrollY;
        const distance = targetY - startY;
        const startTime = Date.now();
        
        const scrollStep = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease-out function for natural scrolling
            const ease = 1 - Math.pow(1 - progress, 3);
            const currentY = startY + distance * ease;
            
            window.scrollTo(0, currentY);
            
            if (progress < 1) {
                requestAnimationFrame(scrollStep);
            }
        };
        
        scrollStep();
        
        // Wait for scroll to complete
        await new Promise(resolve => setTimeout(resolve, duration));
    }
    
    // Simulate human-like clicking
    async humanClick(element, x = null, y = null) {
        if (!this.isEnabled) {
            element.click();
            return;
        }
        
        // Get element position if coordinates not provided
        if (x === null || y === null) {
            const rect = element.getBoundingClientRect();
            x = rect.left + rect.width / 2;
            y = rect.top + rect.height / 2;
        }
        
        // Move mouse to element
        await this.humanMouseMove(
            window.innerWidth / 2,
            window.innerHeight / 2,
            x,
            y
        );
        
        // Small delay before click
        await this.humanDelay(100, 300);
        
        // Click
        element.click();
    }
    
    // Configure interaction parameters
    configure(config) {
        if (config.delay) {
            this.interactionDelay = {
                min: config.delay.min || this.interactionDelay.min,
                max: config.delay.max || this.interactionDelay.max
            };
        }
        
        if (config.mouse) {
            this.mouseMovement = {
                enabled: config.mouse.enabled !== undefined ? config.mouse.enabled : this.mouseMovement.enabled,
                steps: config.mouse.steps || this.mouseMovement.steps,
                variance: config.mouse.variance || this.mouseMovement.variance
            };
        }
    }
    
    // Check if module is enabled
    isEnabled() {
        return this.isEnabled;
    }
}

// Export as singleton
const humanInteraction = new HumanInteractionModule();
export default humanInteraction;
""")
        
        with open(interaction_dir / "human_interaction.js", 'w') as f:
            f.write(human_interaction.render())
```
