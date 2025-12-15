package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
)

// Metrics represents performance metrics collected by the service
type Metrics struct {
	Timestamp         time.Time `json:"timestamp"`
	CPUUsage          float64   `json:"cpu_usage"`
	MemoryUsage       uint64    `json:"memory_usage"`
	Goroutines        int       `json:"goroutines"`
	BuildTime         float64   `json:"build_time_ms"`
	RequestsServed    int64     `json:"requests_served"`
	AverageResponseMs float64   `json:"avg_response_ms"`
}

// PerformanceMonitorService collects and serves performance metrics
type PerformanceMonitorService struct {
	mu             sync.RWMutex
	metrics        Metrics
	requestCount   int64
	totalResponse  time.Duration
	buildStartTime time.Time
	server         *http.Server
}

// NewPerformanceMonitorService creates a new performance monitor service
func NewPerformanceMonitorService() *PerformanceMonitorService {
	return &PerformanceMonitorService{
		metrics: Metrics{
			Timestamp: time.Now(),
		},
	}
}

// StartBuildTimer starts timing a build operation
func (p *PerformanceMonitorService) StartBuildTimer() {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.buildStartTime = time.Now()
}

// EndBuildTimer ends timing a build operation and records the duration
func (p *PerformanceMonitorService) EndBuildTimer() float64 {
	p.mu.Lock()
	defer p.mu.Unlock()

	duration := time.Since(p.buildStartTime).Seconds() * 1000 // Convert to milliseconds
	p.metrics.BuildTime = duration
	return duration
}

// RecordRequest records a request and its response time
func (p *PerformanceMonitorService) RecordRequest(responseTime time.Duration) {
	p.mu.Lock()
	defer p.mu.Unlock()

	p.requestCount++
	p.totalResponse += responseTime

	// Update average response time
	if p.requestCount > 0 {
		p.metrics.AverageResponseMs = float64(p.totalResponse.Milliseconds()) / float64(p.requestCount)
	}

	p.metrics.RequestsServed = p.requestCount
}

// CollectSystemMetrics collects system-level metrics
func (p *PerformanceMonitorService) CollectSystemMetrics() {
	p.mu.Lock()
	defer p.mu.Unlock()

	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	p.metrics.Timestamp = time.Now()
	p.metrics.CPUUsage = 0.0 // Placeholder - would need platform-specific implementation
	p.metrics.MemoryUsage = m.Alloc
	p.metrics.Goroutines = runtime.NumGoroutine()
}

// GetMetrics returns the current metrics
func (p *PerformanceMonitorService) GetMetrics() Metrics {
	p.mu.RLock()
	defer p.mu.RUnlock()
	return p.metrics
}

// StartServer starts the metrics HTTP server
func (p *PerformanceMonitorService) StartServer(port int) error {
	// Set Gin to release mode
	gin.SetMode(gin.ReleaseMode)

	router := gin.New()
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// Metrics endpoint
	router.GET("/metrics", func(c *gin.Context) {
		p.CollectSystemMetrics()
		metrics := p.GetMetrics()
		c.JSON(http.StatusOK, metrics)
	})

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, map[string]string{
			"status":    "ok",
			"timestamp": time.Now().Format(time.RFC3339),
		})
	})

	// Start server in a goroutine
	p.server = &http.Server{
		Addr:    fmt.Sprintf(":%d", port),
		Handler: router,
	}

	log.Printf("📊 Performance monitor server starting on port %d", port)
	return p.server.ListenAndServe()
}

// StopServer stops the metrics HTTP server
func (p *PerformanceMonitorService) StopServer() error {
	if p.server != nil {
		return p.server.Close()
	}
	return nil
}

// SaveMetricsToFile saves metrics to a JSON file
func (p *PerformanceMonitorService) SaveMetricsToFile(projectDir string) error {
	p.CollectSystemMetrics()
	metrics := p.GetMetrics()

	// Create metrics directory if it doesn't exist
	metricsDir := filepath.Join(projectDir, ".flashflow", "metrics")
	if err := os.MkdirAll(metricsDir, 0755); err != nil {
		return err
	}

	// Create filename with timestamp
	filename := fmt.Sprintf("metrics_%s.json", time.Now().Format("20060102_150405"))
	filePath := filepath.Join(metricsDir, filename)

	// Write metrics to file
	data, err := json.MarshalIndent(metrics, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(filePath, data, 0644)
}

func main() {
	// Create performance monitor service
	monitor := NewPerformanceMonitorService()

	// Get port from environment variable or use default
	port := 9090
	if envPort := os.Getenv("PERFORMANCE_MONITOR_PORT"); envPort != "" {
		fmt.Sscanf(envPort, "%d", &port)
	}

	// Start metrics server
	log.Printf("Starting performance monitor on port %d", port)
	if err := monitor.StartServer(port); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Failed to start performance monitor: %v", err)
	}
}
