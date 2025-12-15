package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
)

func main() {
	// Get the current working directory
	cwd, err := os.Getwd()
	if err != nil {
		log.Fatal(err)
	}

	// Services to build
	services := []string{"build-service", "dev-server", "file-watcher", "cli-wrapper"}

	fmt.Println("🏗️  Building all FlashFlow Go services...")

	for _, service := range services {
		fmt.Printf("Building %s...\n", service)

		servicePath := filepath.Join(cwd, service)

		// Change to service directory
		if err := os.Chdir(servicePath); err != nil {
			log.Printf("Failed to change to %s directory: %v", service, err)
			continue
		}

		// Build the service
		cmd := exec.Command("go", "build", "-o", service)

		// On Windows, add .exe extension
		if runtime.GOOS == "windows" {
			cmd.Args = append(cmd.Args, service+".exe")
		}

		// Set environment for consistent builds
		cmd.Env = append(os.Environ(), "CGO_ENABLED=0", "GOOS="+runtime.GOOS, "GOARCH="+runtime.GOARCH)

		// Capture output
		output, err := cmd.CombinedOutput()
		if err != nil {
			fmt.Printf("❌ Failed to build %s: %v\n", service, err)
			fmt.Printf("Output: %s\n", string(output))
			continue
		}

		fmt.Printf("✅ %s built successfully\n", service)

		// Change back to original directory
		if err := os.Chdir(cwd); err != nil {
			log.Printf("Failed to change back to original directory: %v", err)
		}
	}

	fmt.Println("🎉 All FlashFlow Go services built successfully!")
}
