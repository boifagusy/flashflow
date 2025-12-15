package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"text/template"

	"github.com/gin-gonic/gin"
	"gopkg.in/yaml.v2"
)

// FlowFile represents a parsed .flow file
type FlowFile struct {
	Page     *PageDefinition          `yaml:"page,omitempty"`
	Model    map[string]interface{}   `yaml:"model,omitempty"`
	Pages    map[string][]interface{} `yaml:"pages,omitempty"`
	AIModels map[string]interface{}   `yaml:"ai_models,omitempty"`
}

// PageDefinition represents a page in a .flow file
type PageDefinition struct {
	Title string        `yaml:"title,omitempty"`
	Path  string        `yaml:"path,omitempty"`
	Body  []interface{} `yaml:"body,omitempty"`
}

// Component represents a UI component
type Component map[string]interface{}

// DirectRenderer handles rendering .flow files directly
type DirectRenderer struct {
	projectRoot string
	engine      *gin.Engine
}

// NewDirectRenderer creates a new direct renderer
func NewDirectRenderer(projectRoot string) *DirectRenderer {
	// Set Gin to release mode for better performance
	gin.SetMode(gin.ReleaseMode)

	renderer := &DirectRenderer{
		projectRoot: projectRoot,
		engine:      gin.New(),
	}

	// Add middleware
	renderer.engine.Use(gin.Logger())
	renderer.engine.Use(gin.Recovery())

	// Setup routes
	renderer.setupRoutes()

	return renderer
}

// setupRoutes sets up the renderer routes
func (dr *DirectRenderer) setupRoutes() {
	// Serve .flow files directly
	flowsPath := filepath.Join(dr.projectRoot, "src", "flows")
	dr.engine.Static("/flows", flowsPath)

	// API for component rendering
	dr.engine.POST("/api/render/component", dr.renderComponent)

	// Render pages from .flow files - this should be more specific to avoid conflicts
	dr.engine.GET("/", dr.renderPage)
	dr.engine.GET("/app", dr.renderPage)
	dr.engine.GET("/direct-test", dr.renderPage)
	// Add more specific routes as needed
}

// renderPage handles rendering a page from .flow files
func (dr *DirectRenderer) renderPage(c *gin.Context) {
	// Get the request path
	requestPath := c.Request.URL.Path

	// Map routes to .flow files
	pathToFlow := map[string]string{
		"/":            "app",
		"/app":         "app",
		"/direct-test": "direct_test",
	}

	// Get the corresponding .flow file name
	flowFileName, exists := pathToFlow[requestPath]
	if !exists {
		// Default to app.flow
		flowFileName = "app"
	}

	// Try to find the corresponding .flow file
	flowFilePath := filepath.Join(dr.projectRoot, "src", "flows", flowFileName+".flow")
	if _, err := os.Stat(flowFilePath); os.IsNotExist(err) {
		// Try app.flow as fallback
		flowFilePath = filepath.Join(dr.projectRoot, "src", "flows", "app.flow")
	}

	// Parse the .flow file
	flowData, err := dr.parseFlowFile(flowFilePath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": fmt.Sprintf("Failed to parse .flow file: %v", err),
		})
		return
	}

	// Render the page
	html, err := dr.renderFlowToHTML(flowData)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": fmt.Sprintf("Failed to render page: %v", err),
		})
		return
	}

	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}

// parseFlowFile parses a .flow file
func (dr *DirectRenderer) parseFlowFile(filePath string) (*FlowFile, error) {
	// Read file
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read file: %v", err)
	}

	// Parse YAML
	var flowFile FlowFile
	if err := yaml.Unmarshal(data, &flowFile); err != nil {
		return nil, fmt.Errorf("failed to parse YAML: %v", err)
	}

	return &flowFile, nil
}

// renderFlowToHTML renders a FlowFile to HTML
func (dr *DirectRenderer) renderFlowToHTML(flowFile *FlowFile) (string, error) {
	// Simple template for demonstration
	tmpl := `
<!DOCTYPE html>
<html>
<head>
    <title>{{.Title}}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #3B82F6; color: white; padding: 1rem 2rem; border-radius: 8px; margin-bottom: 2rem; }
        .component { background: white; padding: 1.5rem; margin: 1rem 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .button { background: #3B82F6; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; cursor: pointer; font-size: 1rem; }
        .button:hover { background: #2563eb; }
        .card { border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }
        .card-header { background: #f1f5f9; padding: 1rem; font-weight: bold; }
        .card-body { padding: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{.Title}}</h1>
            <p>Directly rendered from .flow file</p>
        </div>
        
        {{range .Components}}
        <div class="component">
            {{if eq .Type "header"}}
                <h2>{{.Content}}</h2>
            {{else if eq .Type "text"}}
                <p>{{.Content}}</p>
            {{else if eq .Type "button"}}
                <button class="button">{{.Text}}</button>
            {{else if eq .Type "card"}}
                <div class="card">
                    <div class="card-header">{{.Title}}</div>
                    <div class="card-body">{{.Content}}</div>
                </div>
            {{else}}
                <div>Unknown component: {{.Type}}</div>
            {{end}}
        </div>
        {{end}}
        
        <div style="margin-top: 2rem; padding: 1rem; background: #fef3c7; border-radius: 8px; border: 1px solid #f59e0b;">
            <h3>🔧 FlashFlow Direct Renderer</h3>
            <p>This page is rendered directly from .flow files without code generation!</p>
            <p><strong>Path:</strong> {{.Path}}</p>
        </div>
    </div>
</body>
</html>
`

	title := "FlashFlow Page"
	if flowFile.Page != nil && flowFile.Page.Title != "" {
		title = flowFile.Page.Title
	}

	components := []map[string]interface{}{}
	if flowFile.Page != nil && flowFile.Page.Body != nil {
		for _, item := range flowFile.Page.Body {
			if comp, ok := item.(map[interface{}]interface{}); ok {
				// Convert map[interface{}]interface{} to map[string]interface{}
				converted := make(map[string]interface{})
				for k, v := range comp {
					if ks, ok := k.(string); ok {
						converted[ks] = v
					}
				}
				components = append(components, converted)
			}
		}
	}

	// Execute template
	t, err := template.New("page").Parse(tmpl)
	if err != nil {
		return "", fmt.Errorf("failed to parse template: %v", err)
	}

	data := map[string]interface{}{
		"Title":      title,
		"Path":       flowFile.Page.Path,
		"Components": components,
	}

	var buf strings.Builder
	if err := t.Execute(&buf, data); err != nil {
		return "", fmt.Errorf("failed to execute template: %v", err)
	}

	return buf.String(), nil
}

// renderComponent handles rendering individual components
func (dr *DirectRenderer) renderComponent(c *gin.Context) {
	var componentData map[string]interface{}
	if err := c.ShouldBindJSON(&componentData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": fmt.Sprintf("Invalid JSON: %v", err),
		})
		return
	}

	// Simple component rendering
	componentType, _ := componentData["type"].(string)
	content, _ := componentData["content"].(string)

	var html string
	switch componentType {
	case "button":
		text, _ := componentData["text"].(string)
		html = fmt.Sprintf(`<button class="button">%s</button>`, text)
	case "card":
		title, _ := componentData["title"].(string)
		html = fmt.Sprintf(`<div class="card"><div class="card-header">%s</div><div class="card-body">%s</div></div>`, title, content)
	default:
		html = fmt.Sprintf(`<div class="component">%s</div>`, content)
	}

	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}

// Start starts the direct renderer server
func (dr *DirectRenderer) Start(host string, port int) error {
	address := fmt.Sprintf("%s:%d", host, port)
	log.Printf("🚀 Starting FlashFlow Direct Renderer on http://%s", address)
	log.Println("📍 Serving .flow files directly without code generation")
	log.Println()
	log.Println("Available routes:")
	log.Printf("   🏠 Root:             http://%s/", address)
	log.Printf("   📁 Flow Files:       http://%s/flows/", address)
	log.Printf("   🎨 Component API:    http://%s/render/component", address)
	log.Println()
	log.Println("👀 Server is running... (Ctrl+C to stop)")

	return dr.engine.Run(address)
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

	// Check if this is a FlashFlow project
	flashflowConfig := filepath.Join(absProjectDir, "flashflow.json")
	if _, err := os.Stat(flashflowConfig); os.IsNotExist(err) {
		log.Fatal("❌ Not in a FlashFlow project directory")
	}

	// Get host and port from environment variables or use defaults
	host := "localhost"
	if envHost := os.Getenv("FLASHFLOW_HOST"); envHost != "" {
		host = envHost
	}

	port := 8011 // Different port to avoid conflict with dev server
	if envPort := os.Getenv("FLASHFLOW_DIRECT_PORT"); envPort != "" {
		fmt.Sscanf(envPort, "%d", &port)
	}

	// Create and start direct renderer
	renderer := NewDirectRenderer(absProjectDir)
	if err := renderer.Start(host, port); err != nil {
		log.Fatalf("❌ Server error: %v", err)
	}
}
