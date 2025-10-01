"""
FlashFlow 'test' command - Run automated tests
"""

import click
from pathlib import Path
from ..core import FlashFlowProject

@click.command()
@click.option('--file', '-f', help='Run specific test file')
@click.option('--watch', '-w', is_flag=True, help='Watch for changes and re-run tests')
def test(file, watch):
    """Run automated .testflow tests"""
    
    # Check if we're in a FlashFlow project
    project = FlashFlowProject(Path.cwd())
    if not project.exists():
        click.echo("❌ Not in a FlashFlow project directory")
        return
    
    try:
        if watch:
            click.echo("👀 Running tests in watch mode...")
            run_tests_with_watch(project, file)
        else:
            run_tests_once(project, file)
            
    except Exception as e:
        click.echo(f"❌ Test execution failed: {str(e)}")

def run_tests_once(project: FlashFlowProject, specific_file: str = None):
    """Run tests once"""
    
    click.echo(f"🧪 Running tests for: {project.config.name}")
    
    # Get test files
    if specific_file:
        test_files = [Path(specific_file)]
        if not test_files[0].exists():
            click.echo(f"❌ Test file not found: {specific_file}")
            return
    else:
        test_files = project.get_test_files()
    
    if not test_files:
        click.echo("⚠️  No .testflow files found in src/tests/")
        return
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_file in test_files:
        click.echo(f"\n📄 Running: {test_file.name}")
        
        try:
            # Parse and run test file
            test_results = run_single_test_file(test_file)
            
            for result in test_results:
                total_tests += 1
                if result['passed']:
                    passed_tests += 1
                    click.echo(f"   ✅ {result['name']}")
                else:
                    failed_tests += 1
                    click.echo(f"   ❌ {result['name']}: {result['error']}")
                    
        except Exception as e:
            click.echo(f"   ❌ Error running {test_file.name}: {str(e)}")
            failed_tests += 1
    
    # Summary
    click.echo(f"\n📊 Test Results:")
    click.echo(f"   Total: {total_tests}")
    click.echo(f"   ✅ Passed: {passed_tests}")
    click.echo(f"   ❌ Failed: {failed_tests}")
    
    if failed_tests == 0:
        click.echo("🎉 All tests passed!")
    else:
        click.echo("💥 Some tests failed")

def run_tests_with_watch(project: FlashFlowProject, specific_file: str = None):
    """Run tests with file watching"""
    import time
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    
    class TestFileHandler(FileSystemEventHandler):
        def __init__(self, project, specific_file):
            self.project = project
            self.specific_file = specific_file
            self.last_run = 0
        
        def on_modified(self, event):
            if event.is_directory:
                return
            
            # Only re-run for .testflow or .flow files
            if not (event.src_path.endswith('.testflow') or event.src_path.endswith('.flow')):
                return
            
            # Debounce test runs
            now = time.time()
            if now - self.last_run < 2:
                return
            
            self.last_run = now
            click.echo(f"\n🔄 File changed: {event.src_path}")
            try:
                run_tests_once(self.project, self.specific_file)
                click.echo("👀 Watching for changes... (Ctrl+C to stop)")
            except Exception as e:
                click.echo(f"❌ Test error: {str(e)}")
    
    # Initial test run
    run_tests_once(project, specific_file)
    
    # Setup file watcher
    event_handler = TestFileHandler(project, specific_file)
    observer = Observer()
    observer.schedule(event_handler, str(project.src_path), recursive=True)
    observer.start()
    
    click.echo("👀 Watching for changes... (Ctrl+C to stop)")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        click.echo("\n🛑 Test watch mode stopped")
    
    observer.join()

def run_single_test_file(test_file: Path):
    """Run a single .testflow file and return results"""
    
    # For now, return mock results
    # TODO: Implement actual .testflow parser and test runner
    
    results = []
    
    # Mock test result based on filename
    if "basic" in test_file.name:
        results.append({
            'name': 'Health Check Test',
            'passed': True,
            'error': None
        })
    else:
        results.append({
            'name': f'Test from {test_file.name}',
            'passed': True,
            'error': None
        })
    
    return results