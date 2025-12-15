package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"time"

	"github.com/spf13/cobra"
)

var (
	// Build command flags
	buildTarget string
	buildEnv    string
	buildWatch  bool

	// Serve command flags
	serveAll  bool
	serveHost string
	servePort int

	// FlashFlow Engine command flags
	fletServeHost  string
	fletServePort  int
	fletBackendURL string
)

func main() {
	var rootCmd = &cobra.Command{
		Use:   "flashflow-go",
		Short: "FlashFlow Go Services CLI",
		Long:  "A high-performance CLI for FlashFlow development services written in Go",
	}

	// Build command
	var buildCmd = &cobra.Command{
		Use:   "build",
		Short: "Build FlashFlow project with Go optimization",
		Long:  "Generate application code from .flow files using optimized Go services",
		Run:   runBuild,
	}

	buildCmd.Flags().StringVarP(&buildTarget, "target", "t", "all", "Build target (all, backend, frontend, mobile, ios, android, desktop, windows, macos, linux)")
	buildCmd.Flags().StringVarP(&buildEnv, "env", "e", "development", "Build environment (development, production)")
	buildCmd.Flags().BoolVarP(&buildWatch, "watch", "w", false, "Watch for file changes and rebuild")

	// Serve command
	var serveCmd = &cobra.Command{
		Use:   "serve",
		Short: "Start development server with Go optimization",
		Long:  "Run unified development server using optimized Go services",
		Run:   runServe,
	}

	serveCmd.Flags().BoolVarP(&serveAll, "all", "a", false, "Serve all components (recommended)")
	serveCmd.Flags().StringVarP(&serveHost, "host", "h", "localhost", "Host to serve on")
	serveCmd.Flags().IntVarP(&servePort, "port", "p", 8000, "Port to serve on")

	// Direct render command
	var directRenderCmd = &cobra.Command{
		Use:   "direct-render",
		Short: "Start direct renderer server",
		Long:  "Run direct renderer server that serves .flow files without code generation",
		Run:   runDirectRender,
	}

	directRenderCmd.Flags().StringVarP(&serveHost, "host", "h", "localhost", "Host to serve on")
	directRenderCmd.Flags().IntVarP(&servePort, "port", "p", 8011, "Port to serve on")

	// FlashFlow Engine command
	var fletDirectRenderCmd = &cobra.Command{
		Use:   "flashflow-engine",
		Short: "Start FlashFlow Engine server",
		Long:  "Run FlashFlow Engine server that serves .flow files without code generation using Python Flet",
		Run:   runFletDirectRender,
	}

	fletDirectRenderCmd.Flags().StringVarP(&fletServeHost, "host", "h", "localhost", "Host to serve on")
	fletDirectRenderCmd.Flags().IntVarP(&fletServePort, "port", "p", 8012, "Port to serve on")
	fletDirectRenderCmd.Flags().StringVarP(&fletBackendURL, "backend", "b", "http://localhost:8000", "Backend URL for API integration")

	// Add commands to root
	rootCmd.AddCommand(buildCmd)
	rootCmd.AddCommand(serveCmd)
	rootCmd.AddCommand(directRenderCmd)
	rootCmd.AddCommand(fletDirectRenderCmd)

	// Execute CLI
	if err := rootCmd.Execute(); err != nil {
		log.Fatal(err)
	}
}

// runBuild executes the build command using the Go build service
func runBuild(cmd *cobra.Command, args []string) {
	// Get current working directory
	cwd, err := os.Getwd()
	if err != nil {
		log.Fatalf("Failed to get current directory: %v", err)
	}

	// Check if this is a FlashFlow project
	flashflowConfig := filepath.Join(cwd, "flashflow.json")
	if _, err := os.Stat(flashflowConfig); os.IsNotExist(err) {
		log.Fatal("❌ Not in a FlashFlow project directory. Run 'flashflow new <project_name>' to create a new project first")
	}

	fmt.Printf("🔨 Building FlashFlow project with Go optimization...\n")
	fmt.Printf("📦 Target: %s\n", buildTarget)
	fmt.Printf("🌍 Environment: %s\n", buildEnv)

	// Determine the path to the build service executable
	buildServicePath := filepath.Join("go-services", "build-service", "build-service")

	// On Windows, add .exe extension
	if isWindows() {
		buildServicePath += ".exe"
	}

	// Check if build service executable exists
	if _, err := os.Stat(buildServicePath); os.IsNotExist(err) {
		// Try to build the service first
		if err := buildGoService("build-service"); err != nil {
			log.Fatalf("Failed to build build service: %v", err)
		}
	}

	// Execute the build service
	buildArgs := []string{cwd}
	if buildWatch {
		buildArgs = append(buildArgs, "--watch")
	}

	buildCmd := exec.Command(buildServicePath, buildArgs...)
	buildCmd.Stdout = os.Stdout
	buildCmd.Stderr = os.Stderr
	buildCmd.Env = append(os.Environ(),
		fmt.Sprintf("FLASHFLOW_TARGET=%s", buildTarget),
		fmt.Sprintf("FLASHFLOW_ENV=%s", buildEnv),
		fmt.Sprintf("FLASHFLOW_WATCH=%t", buildWatch),
	)

	if err := buildCmd.Run(); err != nil {
		log.Fatalf("Build service failed: %v", err)
	}
}

// runServe executes the serve command using the Go development server
func runServe(cmd *cobra.Command, args []string) {
	// Get current working directory
	cwd, err := os.Getwd()
	if err != nil {
		log.Fatalf("Failed to get current directory: %v", err)
	}

	// Check if this is a FlashFlow project
	flashflowConfig := filepath.Join(cwd, "flashflow.json")
	if _, err := os.Stat(flashflowConfig); os.IsNotExist(err) {
		log.Fatal("❌ Not in a FlashFlow project directory")
	}

	fmt.Printf("🚀 Starting FlashFlow development server with Go optimization...\n")
	fmt.Printf("📦 Auto-generating all platform-specific apps before serving...\n")

	// Determine the path to the dev server executable
	devServerPath := filepath.Join("go-services", "dev-server", "dev-server")

	// On Windows, add .exe extension
	if isWindows() {
		devServerPath += ".exe"
	}

	// Check if dev server executable exists
	if _, err := os.Stat(devServerPath); os.IsNotExist(err) {
		// Try to build the service first
		if err := buildGoService("dev-server"); err != nil {
			log.Fatalf("Failed to build dev server: %v", err)
		}
	}

	// Start FlashFlow Engine automatically in the background
	engineProcess, err := startFlashFlowEngine(cwd, serveHost, servePort)
	if err != nil {
		fmt.Printf("⚠️  Warning: Could not start FlashFlow Engine automatically: %v\n", err)
	} else {
		fmt.Printf("⚡ FlashFlow Engine started automatically on http://localhost:8012\n")
		// Give the engine a moment to start
		time.Sleep(2 * time.Second)
	}

	// Execute the dev server
	serveArgs := []string{cwd}

	serveCmd := exec.Command(devServerPath, serveArgs...)
	serveCmd.Stdout = os.Stdout
	serveCmd.Stderr = os.Stderr
	serveCmd.Env = append(os.Environ(),
		fmt.Sprintf("FLASHFLOW_HOST=%s", serveHost),
		fmt.Sprintf("FLASHFLOW_PORT=%d", servePort),
	)

	if err := serveCmd.Run(); err != nil {
		log.Fatalf("Dev server failed: %v", err)
	}

	// Clean up FlashFlow Engine process if it was started
	if engineProcess != nil {
		fmt.Printf("🛑 Stopping FlashFlow Engine...\n")
		engineProcess.Process.Kill()
	}
}

// startFlashFlowEngine starts the FlashFlow Engine in the background
func startFlashFlowEngine(projectDir, host string, port int) (*exec.Cmd, error) {
	// Determine the path to the Flet direct renderer script
	fletRendererPath := filepath.Join("python-services", "flet-direct-renderer", "main.py")

	// Check if Flet renderer script exists
	if _, err := os.Stat(fletRendererPath); os.IsNotExist(err) {
		return nil, fmt.Errorf("FlashFlow Engine not found at %s", fletRendererPath)
	}

	// Prepare arguments for the FlashFlow Engine
	fletRenderArgs := []string{"main.py", projectDir, fmt.Sprintf("http://%s:%d", host, port)}

	// Find Python executable
	pythonCmd := "python"
	if isWindows() {
		pythonCmd = "python.exe"
	}

	// Try python3 first
	cmdPath, err := exec.LookPath("python3")
	if err == nil {
		pythonCmd = cmdPath
	} else {
		// Fall back to python
		cmdPath, err := exec.LookPath("python")
		if err != nil {
			return nil, fmt.Errorf("Python not found in PATH")
		}
		pythonCmd = cmdPath
	}

	// Start the FlashFlow Engine process
	fletRenderCmd := exec.Command(pythonCmd, fletRenderArgs...)
	fletRenderCmd.Dir = filepath.Join("python-services", "flet-direct-renderer")
	fletRenderCmd.Stdout = os.Stdout
	fletRenderCmd.Stderr = os.Stderr
	fletRenderCmd.Stdin = os.Stdin

	// Start the process
	if err := fletRenderCmd.Start(); err != nil {
		return nil, fmt.Errorf("failed to start FlashFlow Engine: %v", err)
	}

	return fletRenderCmd, nil
}

// runDirectRender executes the direct renderer
func runDirectRender(cmd *cobra.Command, args []string) {
	// Get current working directory
	cwd, err := os.Getwd()
	if err != nil {
		log.Fatalf("Failed to get current directory: %v", err)
	}

	// Check if this is a FlashFlow project
	flashflowConfig := filepath.Join(cwd, "flashflow.json")
	if _, err := os.Stat(flashflowConfig); os.IsNotExist(err) {
		log.Fatal("❌ Not in a FlashFlow project directory. Run 'flashflow new <project_name>' to create a new project first")
	}

	fmt.Printf("🚀 Starting FlashFlow Direct Renderer...\n")
	fmt.Printf("🌐 Host: %s\n", serveHost)
	fmt.Printf("🔢 Port: %d\n", servePort)

	// Determine the path to the direct renderer executable
	directRendererPath := filepath.Join("go-services", "direct-renderer", "direct-renderer")

	// On Windows, add .exe extension
	if isWindows() {
		directRendererPath += ".exe"
	}

	// Check if direct renderer executable exists
	if _, err := os.Stat(directRendererPath); os.IsNotExist(err) {
		log.Fatalf("Direct renderer not found at %s. Please build it first with 'python build_go_services.py'", directRendererPath)
	}

	// Execute the direct renderer
	directRenderArgs := []string{}
	if len(args) > 0 {
		directRenderArgs = append(directRenderArgs, args[0])
	} else {
		directRenderArgs = append(directRenderArgs, cwd)
	}

	directRenderCmd := exec.Command(directRendererPath, directRenderArgs...)
	directRenderCmd.Stdout = os.Stdout
	directRenderCmd.Stderr = os.Stderr
	directRenderCmd.Stdin = os.Stdin

	if err := directRenderCmd.Run(); err != nil {
		log.Fatalf("Direct renderer failed: %v", err)
	}
}

// runFletDirectRender executes the FlashFlow Engine
func runFletDirectRender(cmd *cobra.Command, args []string) {
	// Get current working directory
	cwd, err := os.Getwd()
	if err != nil {
		log.Fatalf("Failed to get current directory: %v", err)
	}

	// Check if this is a FlashFlow project
	flashflowConfig := filepath.Join(cwd, "flashflow.json")
	if _, err := os.Stat(flashflowConfig); os.IsNotExist(err) {
		log.Fatal("❌ Not in a FlashFlow project directory. Run 'flashflow new <project_name>' to create a new project first")
	}

	fmt.Printf("🚀 Starting FlashFlow Engine...\n")
	fmt.Printf("🌐 Host: %s\n", fletServeHost)
	fmt.Printf("🔢 Port: %d\n", fletServePort)
	fmt.Printf("📡 Backend URL: %s\n", fletBackendURL)

	// Determine the path to the Flet direct renderer script
	fletRendererPath := filepath.Join("python-services", "flet-direct-renderer", "main.py")

	// Check if Flet renderer script exists
	if _, err := os.Stat(fletRendererPath); os.IsNotExist(err) {
		log.Fatalf("FlashFlow Engine not found at %s", fletRendererPath)
	}

	// Execute the Flet direct renderer
	fletRenderArgs := []string{"main.py"}
	if len(args) > 0 {
		fletRenderArgs = append(fletRenderArgs, args[0])
	} else {
		fletRenderArgs = append(fletRenderArgs, cwd)
	}
	fletRenderArgs = append(fletRenderArgs, fletBackendURL)

	// Find Python executable
	pythonCmd := "python"
	if isWindows() {
		pythonCmd = "python.exe"
	}

	// Try python3 first
	cmdPath, err := exec.LookPath("python3")
	if err == nil {
		pythonCmd = cmdPath
	} else {
		// Fall back to python
		cmdPath, err := exec.LookPath("python")
		if err != nil {
			log.Fatal("Python not found in PATH")
		}
		pythonCmd = cmdPath
	}

	fletRenderCmd := exec.Command(pythonCmd, fletRenderArgs...)
	fletRenderCmd.Dir = filepath.Join("python-services", "flet-direct-renderer")
	fletRenderCmd.Stdout = os.Stdout
	fletRenderCmd.Stderr = os.Stderr
	fletRenderCmd.Stdin = os.Stdin

	if err := fletRenderCmd.Run(); err != nil {
		log.Fatalf("Flet direct renderer failed: %v", err)
	}
}

// buildGoService builds a Go service
func buildGoService(serviceName string) error {
	fmt.Printf("🏗️  Building %s service...\n", serviceName)

	servicePath := filepath.Join("go-services", serviceName)

	// Change to service directory
	oldWd, err := os.Getwd()
	if err != nil {
		return err
	}

	if err := os.Chdir(servicePath); err != nil {
		return err
	}

	// Defer changing back to original directory
	defer os.Chdir(oldWd)

	// Build the service
	buildCmd := exec.Command("go", "build", "-o", serviceName)
	if isWindows() {
		buildCmd.Args = append(buildCmd.Args, serviceName+".exe")
	}

	buildCmd.Stdout = os.Stdout
	buildCmd.Stderr = os.Stderr

	if err := buildCmd.Run(); err != nil {
		return fmt.Errorf("failed to build %s: %v", serviceName, err)
	}

	// Move the built executable to the correct location
	executableName := serviceName
	if isWindows() {
		executableName += ".exe"
	}

	// Copy the executable to the service directory
	if err := os.Rename(executableName, filepath.Join("..", serviceName, executableName)); err != nil {
		return err
	}

	fmt.Printf("✅ %s service built successfully\n", serviceName)
	return nil
}

// isWindows checks if the current OS is Windows
func isWindows() bool {
	return os.PathSeparator == '\\' && os.PathListSeparator == ';'
}
