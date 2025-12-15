package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
)

// FlashFlowConfig represents the FlashFlow project configuration
type FlashFlowConfig struct {
	Name         string            `json:"name"`
	Version      string            `json:"version"`
	Description  string            `json:"description"`
	Author       string            `json:"author"`
	Frameworks   map[string]string `json:"frameworks"`
	Dependencies []string          `json:"dependencies"`
}

// FlashFlowProject represents a FlashFlow project
type FlashFlowProject struct {
	RootPath   string
	ConfigPath string
	SrcPath    string
	FlowsPath  string
	DistPath   string
	Config     FlashFlowConfig
}

// NewFlashFlowProject creates a new FlashFlow project instance
func NewFlashFlowProject(rootPath string) (*FlashFlowProject, error) {
	project := &FlashFlowProject{
		RootPath:   rootPath,
		ConfigPath: filepath.Join(rootPath, "flashflow.json"),
		SrcPath:    filepath.Join(rootPath, "src"),
		FlowsPath:  filepath.Join(rootPath, "src", "flows"),
		DistPath:   filepath.Join(rootPath, "dist"),
	}

	// Load configuration
	if err := project.loadConfig(); err != nil {
		return nil, err
	}

	return project, nil
}

// loadConfig loads the FlashFlow project configuration
func (p *FlashFlowProject) loadConfig() error {
	// Check if config file exists
	if _, err := os.Stat(p.ConfigPath); os.IsNotExist(err) {
		return fmt.Errorf("flashflow.json not found in %s", p.RootPath)
	}

	// Read config file
	data, err := ioutil.ReadFile(p.ConfigPath)
	if err != nil {
		return fmt.Errorf("failed to read flashflow.json: %v", err)
	}

	// Parse JSON
	if err := json.Unmarshal(data, &p.Config); err != nil {
		return fmt.Errorf("failed to parse flashflow.json: %v", err)
	}

	return nil
}

// exists checks if this is a valid FlashFlow project
func (p *FlashFlowProject) exists() bool {
	_, err := os.Stat(p.ConfigPath)
	return err == nil
}

// DevServer represents the FlashFlow development server
type DevServer struct {
	project *FlashFlowProject
	engine  *gin.Engine
	host    string
	port    int
	clients map[string]chan struct{}
	mu      sync.Mutex
}

// NewDevServer creates a new development server instance
func NewDevServer(project *FlashFlowProject, host string, port int) *DevServer {
	// Set Gin to release mode for better performance
	gin.SetMode(gin.ReleaseMode)

	// Automatically build all platform-specific apps before starting the server
	if err := buildAllPlatforms(project.RootPath); err != nil {
		log.Printf("⚠️  Warning: Failed to build all platforms: %v", err)
	}

	server := &DevServer{
		project: project,
		engine:  gin.New(),
		host:    host,
		port:    port,
		clients: make(map[string]chan struct{}),
	}

	// Add middleware
	server.engine.Use(gin.Logger())
	server.engine.Use(gin.Recovery())

	// Setup routes
	server.setupRoutes()

	return server
}

// buildAllPlatforms builds all platform-specific apps using the Go build service
func buildAllPlatforms(projectDir string) error {
	log.Println("🔨 Building all platform-specific apps...")

	// Determine the path to the build service executable
	buildServicePath := filepath.Join("go-services", "build-service", "build-service")

	// On Windows, add .exe extension
	if isWindows() {
		buildServicePath += ".exe"
	}

	// Check if build service executable exists
	if _, err := os.Stat(buildServicePath); os.IsNotExist(err) {
		return fmt.Errorf("build service not found at %s", buildServicePath)
	}

	// Execute the build service with "all" target
	buildArgs := []string{projectDir}

	buildCmd := exec.Command(buildServicePath, buildArgs...)
	buildCmd.Env = append(os.Environ(),
		"FLASHFLOW_TARGET=all",
		"FLASHFLOW_ENV=development",
	)

	// Capture output
	output, err := buildCmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("build service failed: %v\nOutput: %s", err, string(output))
	}

	log.Println("✅ All platform-specific apps built successfully")
	return nil
}

// isWindows checks if the current OS is Windows
func isWindows() bool {
	return os.PathSeparator == '\\' && os.PathListSeparator == ';'
}

// setupRoutes sets up all the server routes
func (s *DevServer) setupRoutes() {
	// Welcome page
	s.engine.GET("/", s.welcomeHandler)

	// Dashboard
	s.engine.GET("/dashboard", s.dashboardHandler)

	// Admin panel
	s.engine.GET("/admin/cpanel", s.adminPanelHandler)

	// API documentation
	s.engine.GET("/api/docs", s.apiDocsHandler)

	// API tester
	s.engine.GET("/api/tester", s.apiTesterHandler)

	// API health endpoint
	s.engine.GET("/api/health", s.apiHealthHandler)

	// Mobile previews
	s.engine.GET("/android", s.androidPreviewHandler)
	s.engine.GET("/ios", s.iosPreviewHandler)

	// Desktop preview
	s.engine.GET("/desktop", s.desktopPreviewHandler)

	// Backend status
	s.engine.GET("/backend", s.backendStatusHandler)

	// Hot reload endpoint
	s.engine.POST("/__reload", s.reloadHandler)

	// Serve static files from dist directory
	s.engine.Static("/dist", s.project.DistPath)

	// Serve static files from assets directory
	assetsPath := filepath.Join(s.project.SrcPath, "assets")
	if _, err := os.Stat(assetsPath); err == nil {
		s.engine.Static("/assets", assetsPath)
	}
}

// welcomeHandler handles the welcome page
func (s *DevServer) welcomeHandler(c *gin.Context) {
	html := fmt.Sprintf(`
<!DOCTYPE html>
<html>
<head>
    <title>%s - FlashFlow</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%%, #764ba2 100%%); color: white; }
        .container { max-width: 800px; margin: 0 auto; padding: 60px 20px; text-align: center; }
        h1 { font-size: 3rem; margin-bottom: 0.5rem; font-weight: 300; }
        .subtitle { font-size: 1.2rem; opacity: 0.9; margin-bottom: 3rem; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 40px 0; }
        .card { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 10px; backdrop-filter: blur(10px); }
        .card h3 { margin-top: 0; }
        a { color: white; text-decoration: none; font-weight: 500; }
        a:hover { text-decoration: underline; }
        .version { opacity: 0.7; font-size: 0.9rem; margin-top: 2rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>%s</h1>
        <p class="subtitle">Built with FlashFlow - Single-syntax full-stack development</p>
        
        <div class="grid">
            <div class="card">
                <h3>📊 Dashboard</h3>
                <p><a href="/dashboard">User Dashboard</a></p>
            </div>
            <div class="card">
                <h3>👨‍💼 Admin</h3>
                <p><a href="/admin/cpanel">Admin Panel</a></p>
            </div>
            <div class="card">
                <h3>📚 API</h3>
                <p><a href="/api/docs">Documentation</a> | <a href="/api/tester">Tester</a></p>
            </div>
            <div class="card">
                <h3>📱 Mobile</h3>
                <p><a href="/android">Android</a> | <a href="/ios">iOS</a></p>
            </div>
            <div class="card">
                <h3>🖥️ Desktop</h3>
                <p><a href="/desktop">Desktop Preview</a></p>
            </div>
            <div class="card">
                <h3>🔧 Backend</h3>
                <p><a href="/backend">Status</a></p>
            </div>
        </div>
        
        <div class="version">
            FlashFlow v0.1 | Project: %s
        </div>
    </div>
</body>
</html>
`, s.project.Config.Name, s.project.Config.Name, s.project.Config.Name)

	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}

// dashboardHandler handles the dashboard page
func (s *DevServer) dashboardHandler(c *gin.Context) {
	html := fmt.Sprintf(`
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - %s</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8f9fa; }
        .header { background: #3B82F6; color: white; padding: 1rem 2rem; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav { background: white; padding: 1rem 2rem; margin-bottom: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav a { margin-right: 2rem; color: #3B82F6; text-decoration: none; }
        .nav a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Dashboard</h1>
    </div>
    <div class="container">
        <div class="nav">
            <a href="/dashboard">Home</a>
            <a href="/profile">Profile</a>
            <a href="/settings">Settings</a>
            <a href="/">← Back to Welcome</a>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Welcome</h3>
                <p>FlashFlow User</p>
            </div>
            <div class="stat-card">
                <h3>Status</h3>
                <p>Active</p>
            </div>
            <div class="stat-card">
                <h3>Project</h3>
                <p>%s</p>
            </div>
        </div>
        
        <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h2>Dashboard Content</h2>
            <p>This dashboard is generated from your .flow files. Add more components and data models to see them here.</p>
        </div>
    </div>
</body>
</html>
`, s.project.Config.Name, s.project.Config.Name)

	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}

// adminPanelHandler handles the admin panel page
func (s *DevServer) adminPanelHandler(c *gin.Context) {
	html := fmt.Sprintf(`
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel - %s</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #1a1a1a; color: white; }
        .header { background: #2d3748; padding: 1rem 2rem; border-bottom: 1px solid #4a5568; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .admin-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .admin-card { background: #2d3748; padding: 2rem; border-radius: 8px; border: 1px solid #4a5568; }
        .admin-card h3 { margin-top: 0; color: #63b3ed; }
        a { color: #63b3ed; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛠️ Admin Panel</h1>
        <p>Manage your %s application</p>
    </div>
    <div class="container">
        <div class="admin-grid">
            <div class="admin-card">
                <h3>📊 Database</h3>
                <p>Manage models and data</p>
                <a href="/admin/database">View Database →</a>
            </div>
            <div class="admin-card">
                <h3>👥 Users</h3>
                <p>User management</p>
                <a href="/admin/users">Manage Users →</a>
            </div>
            <div class="admin-card">
                <h3>⚙️ Settings</h3>
                <p>Application configuration</p>
                <a href="/admin/settings">Settings →</a>
            </div>
            <div class="admin-card">
                <h3>📈 Analytics</h3>
                <p>Usage statistics</p>
                <a href="/admin/analytics">View Analytics →</a>
            </div>
        </div>
        
        <div style="margin-top: 2rem; padding: 2rem; background: #2d3748; border-radius: 8px; border: 1px solid #4a5568;">
            <h2>Quick Actions</h2>
            <p><a href="/api/docs">📚 API Documentation</a> | <a href="/api/tester">🧪 API Tester</a> | <a href="/">🏠 Back to App</a></p>
        </div>
    </div>
</body>
</html>
`, s.project.Config.Name, s.project.Config.Name)

	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}

// apiDocsHandler handles the API documentation page
func (s *DevServer) apiDocsHandler(c *gin.Context) {
	html := fmt.Sprintf(`
<!DOCTYPE html>
<html>
<head>
    <title>API Documentation - %s</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8f9fa; }
        .container { max-width: 1000px; margin: 0 auto; padding: 2rem; }
        .endpoint { background: white; margin: 1rem 0; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .method { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: bold; font-size: 0.8rem; }
        .get { background: #d4edda; color: #155724; }
        .post { background: #fff3cd; color: #856404; }
        .put { background: #cce5ff; color: #004085; }
        .delete { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 API Documentation</h1>
        <p>Auto-generated API documentation for %s</p>
        
        <div class="endpoint">
            <h3><span class="method get">GET</span> /api/health</h3>
            <p><strong>Description:</strong> Health check endpoint</p>
            <p><strong>Response:</strong> <code>{"status": "ok", "timestamp": "..."}</code></p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method get">GET</span> /api/todos</h3>
            <p><strong>Description:</strong> Get all todos</p>
            <p><strong>Response:</strong> Array of todo objects</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method post">POST</span> /api/todos</h3>
            <p><strong>Description:</strong> Create a new todo</p>
            <p><strong>Body:</strong> <code>{"task_name": "string"}</code></p>
            <p><strong>Response:</strong> Created todo object</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method put">PUT</span> /api/todos/:id</h3>
            <p><strong>Description:</strong> Update a todo</p>
            <p><strong>Body:</strong> <code>{"is_completed": "boolean"}</code></p>
            <p><strong>Response:</strong> Updated todo object</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method delete">DELETE</span> /api/todos/:id</h3>
            <p><strong>Description:</strong> Delete a todo</p>
            <p><strong>Response:</strong> <code>{"message": "Todo deleted"}</code></p>
        </div>
        
        <p><a href="/api/tester">🧪 Test these endpoints →</a> | <a href="/">🏠 Back to App</a></p>
    </div>
</body>
</html>
`, s.project.Config.Name, s.project.Config.Name)

	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}

// apiTesterHandler handles the API tester page
func (s *DevServer) apiTesterHandler(c *gin.Context) {
	html := fmt.Sprintf(`
<!DOCTYPE html>
<html>
<head>
    <title>API Tester - %s</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8f9fa; }
        .container { max-width: 1000px; margin: 0 auto; padding: 2rem; }
        .tester { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        select, input, textarea, button { margin: 0.5rem 0; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; width: 100%%; box-sizing: border-box; }
        button { background: #3B82F6; color: white; border: none; cursor: pointer; width: auto; padding: 0.5rem 1rem; }
        button:hover { background: #2563eb; }
        .response { background: #f8f9fa; padding: 1rem; margin-top: 1rem; border-radius: 4px; white-space: pre-wrap; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 API Tester</h1>
        <p>Test your FlashFlow API endpoints</p>
        
        <div class="tester">
            <div style="display: grid; grid-template-columns: 100px 1fr; gap: 10px; align-items: center;">
                <select id="method">
                    <option>GET</option>
                    <option>POST</option>
                    <option>PUT</option>
                    <option>DELETE</option>
                </select>
                <input type="text" id="url" placeholder="/api/endpoint" value="/api/health">
            </div>
            
            <textarea id="body" placeholder="Request body (JSON)" rows="4"></textarea>
            
            <button onclick="sendRequest()">Send Request</button>
            
            <div id="response" class="response">Response will appear here...</div>
        </div>
        
        <p><a href="/api/docs">📚 View API Documentation</a> | <a href="/">🏠 Back to App</a></p>
    </div>
    
    <script>
        async function sendRequest() {
            const method = document.getElementById('method').value;
            const url = document.getElementById('url').value;
            const body = document.getElementById('body').value;
            const responseDiv = document.getElementById('response');
            
            try {
                responseDiv.textContent = 'Sending request...';
                
                const options = {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json'
                    }
                };
                
                if (body && method !== 'GET') {
                    options.body = body;
                }
                
                const response = await fetch(url, options);
                const text = await response.text();
                
                responseDiv.textContent = 'Status: ' + response.status + '\\n\\n' + text;
            } catch (error) {
                responseDiv.textContent = 'Error: ' + error.message;
            }
        }
    </script>
</body>
</html>
`, s.project.Config.Name)

	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}

// apiHealthHandler handles the API health endpoint
func (s *DevServer) apiHealthHandler(c *gin.Context) {
	response := map[string]interface{}{
		"status":    "ok",
		"timestamp": time.Now().Format(time.RFC3339),
		"project":   s.project.Config.Name,
		"version":   "0.1.0",
	}
	c.JSON(http.StatusOK, response)
}

// androidPreviewHandler handles the Android preview page
func (s *DevServer) androidPreviewHandler(c *gin.Context) {
	html := `
<!DOCTYPE html>
<html>
<head>
    <title>Android Preview</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f0f0f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .phone { width: 300px; height: 600px; background: black; border-radius: 25px; padding: 20px; position: relative; }
        .screen { width: 100%; height: 100%; background: white; border-radius: 15px; overflow: hidden; position: relative; }
        .status-bar { height: 30px; background: #a4c639; color: white; display: flex; align-items: center; justify-content: space-between; padding: 0 15px; font-size: 0.8rem; }
        .content { padding: 20px; }
        .back-btn { position: absolute; top: 20px; left: 20px; background: white; padding: 10px 20px; border-radius: 20px; text-decoration: none; color: black; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .auth-components { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <a href="/" class="back-btn">← Back</a>
    <div class="phone">
        <div class="screen">
            <div class="status-bar">
                <span>9:41</span>
                <span>Android App</span>
                <span>🔋 100%</span>
            </div>
            <div class="content">
                <h2>📱 Android App Preview</h2>
                <p>This is a mockup of your FlashFlow app running on Android.</p>
                <p>The actual native app will be generated from your .flow files.</p>
                
                <div class="auth-components">
                    <h4>Shared Authentication Components:</h4>
                    <ul>
                        <li>AuthService - Cross-platform authentication service</li>
                        <li>AuthForm - Reusable login/registration UI</li>
                        <li>Token management - Automatic token handling</li>
                        <li>Password validation - Consistent security rules</li>
                    </ul>
                </div>
                
                <button style="width: 100%; padding: 15px; background: #a4c639; color: white; border: none; border-radius: 8px; font-size: 1rem;">
                    Sample Button
                </button>
            </div>
        </div>
    </div>
</body>
</html>
`
	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}

// iosPreviewHandler handles the iOS preview page
func (s *DevServer) iosPreviewHandler(c *gin.Context) {
	html := `
<!DOCTYPE html>
<html>
<head>
    <title>iOS Preview</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f0f0f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .phone { width: 300px; height: 600px; background: black; border-radius: 25px; padding: 20px; position: relative; }
        .screen { width: 100%; height: 100%; background: white; border-radius: 15px; overflow: hidden; position: relative; }
        .status-bar { height: 30px; background: #007AFF; color: white; display: flex; align-items: center; justify-content: space-between; padding: 0 15px; font-size: 0.8rem; }
        .content { padding: 20px; }
        .back-btn { position: absolute; top: 20px; left: 20px; background: white; padding: 10px 20px; border-radius: 20px; text-decoration: none; color: black; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .auth-components { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <a href="/" class="back-btn">← Back</a>
    <div class="phone">
        <div class="screen">
            <div class="status-bar">
                <span>9:41</span>
                <span>iOS App</span>
                <span>🔋 100%</span>
            </div>
            <div class="content">
                <h2>🍎 iOS App Preview</h2>
                <p>This is a mockup of your FlashFlow app running on iOS.</p>
                <p>The actual native app will be generated from your .flow files.</p>
                
                <div class="auth-components">
                    <h4>Shared Authentication Components:</h4>
                    <ul>
                        <li>AuthService - Cross-platform authentication service</li>
                        <li>AuthForm - Reusable login/registration UI</li>
                        <li>Token management - Automatic token handling</li>
                        <li>Password validation - Consistent security rules</li>
                    </ul>
                </div>
                
                <button style="width: 100%; padding: 15px; background: #007AFF; color: white; border: none; border-radius: 8px; font-size: 1rem;">
                    Sample Button
                </button>
            </div>
        </div>
    </div>
</body>
</html>
`
	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}

// desktopPreviewHandler handles the desktop preview page
func (s *DevServer) desktopPreviewHandler(c *gin.Context) {
	html := `
<!DOCTYPE html>
<html>
<head>
    <title>Desktop Preview</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f0f0f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .desktop { width: 800px; height: 600px; background: #2d3748; border-radius: 8px; padding: 20px; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .title-bar { height: 30px; background: #1a202c; border-radius: 6px 6px 0 0; display: flex; align-items: center; padding: 0 10px; }
        .window-controls { display: flex; margin-right: 10px; }
        .window-button { width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .close { background: #ff5f56; }
        .minimize { background: #ffbd2e; }
        .maximize { background: #27c93f; }
        .window-title { color: #e2e8f0; font-size: 0.8rem; flex: 1; text-align: center; }
        .screen { width: 100%; height: calc(100% - 30px); background: white; border-radius: 0 0 6px 6px; overflow: hidden; position: relative; }
        .menu-bar { height: 30px; background: #f1f5f9; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; padding: 0 15px; font-size: 0.8rem; }
        .menu-item { margin-right: 20px; color: #475569; }
        .content { padding: 20px; }
        .back-btn { position: absolute; top: 50px; left: 20px; background: white; padding: 10px 20px; border-radius: 20px; text-decoration: none; color: black; box-shadow: 0 2px 10px rgba(0,0,0,0.1); z-index: 10; }
    </style>
</head>
<body>
    <a href="/" class="back-btn">← Back</a>
    <div class="desktop">
        <div class="title-bar">
            <div class="window-controls">
                <div class="window-button close"></div>
                <div class="window-button minimize"></div>
                <div class="window-button maximize"></div>
            </div>
            <div class="window-title">Desktop App Preview</div>
        </div>
        <div class="screen">
            <div class="menu-bar">
                <div class="menu-item">File</div>
                <div class="menu-item">Edit</div>
                <div class="menu-item">View</div>
                <div class="menu-item">Help</div>
            </div>
            <div class="content">
                <h2>🖥️ Desktop App Preview</h2>
                <p>This is a mockup of your FlashFlow app running on Desktop.</p>
                <p>The actual desktop app will be generated from your .flow files.</p>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4>Features:</h4>
                    <ul>
                        <li>Cross-platform desktop application</li>
                        <li>Native OS integration</li>
                        <li>Offline capabilities</li>
                        <li>Auto-updates</li>
                    </ul>
                </div>
                
                <button style="width: 100%; padding: 15px; background: #3B82F6; color: white; border: none; border-radius: 8px; font-size: 1rem;">
                    Sample Button
                </button>
            </div>
        </div>
    </div>
</body>
</html>
`
	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}

// backendStatusHandler handles the backend status page
func (s *DevServer) backendStatusHandler(c *gin.Context) {
	html := fmt.Sprintf(`
<!DOCTYPE html>
<html>
<head>
    <title>Backend Status - %s</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8f9fa; }
        .container { max-width: 800px; margin: 0 auto; padding: 2rem; }
        .status { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 1rem 0; }
        .healthy { border-left: 4px solid #10b981; }
        .metric { display: flex; justify-content: space-between; margin: 0.5rem 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Backend Status</h1>
        
        <div class="status healthy">
            <h3>✅ System Health</h3>
            <div class="metric"><span>Status:</span><span>Healthy</span></div>
            <div class="metric"><span>Uptime:</span><span>Running</span></div>
            <div class="metric"><span>Database:</span><span>Connected</span></div>
        </div>
        
        <div class="status">
            <h3>📊 Project Info</h3>
            <div class="metric"><span>Name:</span><span>%s</span></div>
            <div class="metric"><span>Framework:</span><span>FlashFlow</span></div>
            <div class="metric"><span>Environment:</span><span>Development</span></div>
        </div>
        
        <p><a href="/api/docs">📚 API Docs</a> | <a href="/">🏠 Back to App</a></p>
    </div>
</body>
</html>
`, s.project.Config.Name, s.project.Config.Name)

	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}

// reloadHandler handles hot reload notifications
func (s *DevServer) reloadHandler(c *gin.Context) {
	// Notify all connected clients to reload
	s.mu.Lock()
	for id, ch := range s.clients {
		select {
		case ch <- struct{}{}:
		default:
			// If channel is full, remove the client
			close(ch)
			delete(s.clients, id)
		}
	}
	s.mu.Unlock()

	c.JSON(http.StatusOK, map[string]string{"status": "reload triggered"})
}

// Start starts the development server using Gin
func (s *DevServer) Start() error {
	address := fmt.Sprintf("%s:%d", s.host, s.port)
	log.Printf("🚀 Starting FlashFlow unified server for: %s", s.project.Config.Name)
	log.Printf("🌐 Unified server starting on http://%s", address)
	log.Println()
	log.Println("📍 Available routes:")
	log.Printf("   🏠 Welcome Page:     http://%s/", address)
	log.Printf("   📊 Dashboard:        http://%s/dashboard", address)
	log.Printf("   👨‍💼 Admin Panel:      http://%s/admin/cpanel", address)
	log.Printf("   📚 API Docs:         http://%s/api/docs", address)
	log.Printf("   🧪 API Tester:       http://%s/api/tester", address)
	log.Printf("   📱 Android Preview:  http://%s/android", address)
	log.Printf("   🍎 iOS Preview:      http://%s/ios", address)
	log.Printf("   🖥️  Desktop Preview:   http://%s/desktop", address)
	log.Printf("   🔧 Backend Status:   http://%s/backend", address)
	log.Println()
	log.Println("👀 Server is running... (Ctrl+C to stop)")

	return s.engine.Run(address)
}

func main() {
	// Get project directory from command line argument or use current directory
	projectDir := "."
	if len(os.Args) > 1 {
		projectDir = os.Args[1]
	}

	// Resolve to absolute path
	absProjectDir, err := filepath.Abs(projectDir)
	if err != nil {
		log.Fatalf("Failed to resolve project directory: %v", err)
	}

	// Create FlashFlow project instance
	project, err := NewFlashFlowProject(absProjectDir)
	if err != nil {
		log.Fatalf("❌ Failed to initialize FlashFlow project: %v", err)
	}

	// Check if this is a valid FlashFlow project
	if !project.exists() {
		log.Fatal("❌ Not in a FlashFlow project directory")
	}

	// Get host and port from environment variables or use defaults
	host := "localhost"
	if envHost := os.Getenv("FLASHFLOW_HOST"); envHost != "" {
		host = envHost
	}

	port := 8000
	if envPort := os.Getenv("FLASHFLOW_PORT"); envPort != "" {
		fmt.Sscanf(envPort, "%%d", &port)
	}

	// Create and start development server
	server := NewDevServer(project, host, port)
	if err := server.Start(); err != nil {
		log.Fatalf("❌ Server error: %v", err)
	}
}
