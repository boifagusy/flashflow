package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/fsnotify/fsnotify"
)

// FileWatcherService watches for file changes and triggers rebuilds
type FileWatcherService struct {
	watcher       *fsnotify.Watcher
	projectDir    string
	lastBuild     time.Time
	devServerPort int
}

// NewFileWatcherService creates a new file watcher service
func NewFileWatcherService(projectDir string, devServerPort int) (*FileWatcherService, error) {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		return nil, fmt.Errorf("failed to create file watcher: %v", err)
	}

	return &FileWatcherService{
		watcher:       watcher,
		projectDir:    projectDir,
		lastBuild:     time.Now(),
		devServerPort: devServerPort,
	}, nil
}

// StartWatching starts watching for file changes
func (fw *FileWatcherService) StartWatching() error {
	// Add src/flows directory to watcher
	flowsPath := filepath.Join(fw.projectDir, "src", "flows")
	if err := fw.watcher.Add(flowsPath); err != nil {
		log.Printf("Warning: failed to add flows directory to watcher: %v", err)
	}

	// Add src directory to watcher for other file types
	srcPath := filepath.Join(fw.projectDir, "src")
	if err := fw.watcher.Add(srcPath); err != nil {
		log.Printf("Warning: failed to add src directory to watcher: %v", err)
	}

	// Add assets directory if it exists
	assetsPath := filepath.Join(fw.projectDir, "src", "assets")
	if _, err := os.Stat(assetsPath); err == nil {
		if err := fw.watcher.Add(assetsPath); err != nil {
			log.Printf("Warning: failed to add assets directory to watcher: %v", err)
		}
	}

	log.Println("👀 Watching for changes... (Ctrl+C to stop)")

	// Start watching in a goroutine
	go fw.watchFiles()

	return nil
}

// watchFiles watches for file changes and triggers actions
func (fw *FileWatcherService) watchFiles() {
	defer fw.watcher.Close()

	for {
		select {
		case event, ok := <-fw.watcher.Events:
			if !ok {
				return
			}

			// Only rebuild for relevant files
			if fw.shouldRebuild(event.Name) {
				// Debounce builds (max once per second)
				if time.Since(fw.lastBuild) < time.Second {
					continue
				}

				fw.lastBuild = time.Now()
				log.Printf("🔄 File changed: %s", event.Name)

				// Trigger rebuild
				if err := fw.triggerRebuild(event.Name); err != nil {
					log.Printf("❌ Rebuild error: %v", err)
				} else {
					log.Println("✅ Rebuild completed successfully")
					// Notify dev server to reload
					fw.notifyDevServer()
				}
			}

		case err, ok := <-fw.watcher.Errors:
			if !ok {
				return
			}
			log.Printf("❌ Watcher error: %v", err)
		}
	}
}

// shouldRebuild determines if a file change should trigger a rebuild
func (fw *FileWatcherService) shouldRebuild(filename string) bool {
	// Check for .flow files
	if strings.HasSuffix(filename, ".flow") {
		return true
	}

	// Check for asset files that might affect the build
	extensions := []string{".css", ".js", ".html", ".json", ".yaml", ".yml"}
	for _, ext := range extensions {
		if strings.HasSuffix(filename, ext) {
			return true
		}
	}

	return false
}

// triggerRebuild triggers a rebuild of the project
func (fw *FileWatcherService) triggerRebuild(changedFile string) error {
	log.Printf("🔨 Rebuilding project due to change in %s", filepath.Base(changedFile))

	// Determine the path to the build service executable
	buildServicePath := filepath.Join("..", "build-service", "build-service")

	// On Windows, add .exe extension
	if isWindows() {
		buildServicePath += ".exe"
	}

	// Check if build service executable exists
	if _, err := os.Stat(buildServicePath); os.IsNotExist(err) {
		return fmt.Errorf("build service executable not found at %s", buildServicePath)
	}

	// Execute the build service
	buildArgs := []string{fw.projectDir}

	buildCmd := exec.Command(buildServicePath, buildArgs...)
	buildCmd.Stdout = os.Stdout
	buildCmd.Stderr = os.Stderr
	buildCmd.Env = append(os.Environ(),
		"FLASHFLOW_TARGET=all",
		"FLASHFLOW_ENV=development",
	)

	if err := buildCmd.Run(); err != nil {
		return fmt.Errorf("build service failed: %v", err)
	}

	return nil
}

// notifyDevServer notifies the development server to reload
func (fw *FileWatcherService) notifyDevServer() error {
	// Send a reload signal to the dev server
	reloadURL := fmt.Sprintf("http://localhost:%d/__reload", fw.devServerPort)

	// Create a simple HTTP client with timeout
	client := &http.Client{
		Timeout: 5 * time.Second,
	}

	// Send POST request to trigger reload
	resp, err := client.Post(reloadURL, "application/json", nil)
	if err != nil {
		log.Printf("Warning: failed to notify dev server: %v", err)
		return nil // Don't fail the entire process if notification fails
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		log.Println("🔄 Dev server notified to reload")
	} else {
		log.Printf("Warning: dev server returned status %d", resp.StatusCode)
	}

	return nil
}

// isWindows checks if the current OS is Windows
func isWindows() bool {
	return os.PathSeparator == '\\' && os.PathListSeparator == ';'
}

func main() {
	// Get project directory from command line argument or use current directory
	projectDir := "."
	if len(os.Args) > 1 {
		projectDir = os.Args[1]
	}

	// Get dev server port from command line argument or use default
	devServerPort := 8000
	if len(os.Args) > 2 {
		fmt.Sscanf(os.Args[2], "%d", &devServerPort)
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

	// Create file watcher service
	fileWatcher, err := NewFileWatcherService(absProjectDir, devServerPort)
	if err != nil {
		log.Fatalf("❌ Failed to create file watcher: %v", err)
	}

	// Start watching
	if err := fileWatcher.StartWatching(); err != nil {
		log.Fatalf("❌ Failed to start file watching: %v", err)
	}

	// Block forever
	select {}
}
