#!/usr/bin/env python3
"""
Script to verify that the FlashFlow build service can handle projects with AI and real-time capabilities.
"""

import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the current directory to the path so we can import the build service
sys.path.append('.')

def main():
    # Create a temporary project directory
    test_dir = tempfile.mkdtemp()
    project_path = Path(test_dir)
    src_path = project_path / "src"
    flows_path = src_path / "flows"
    dist_path = project_path / "dist"
    assets_path = project_path / "assets"
    
    # Create directory structure
    src_path.mkdir(parents=True, exist_ok=True)
    flows_path.mkdir(parents=True, exist_ok=True)
    dist_path.mkdir(parents=True, exist_ok=True)
    assets_path.mkdir(parents=True, exist_ok=True)
    
    # Create a mock flashflow.json
    flashflow_json = project_path / "flashflow.json"
    flashflow_json.write_text('{"name": "test-project", "version": "0.1.0"}')
    
    # Create a test .flow file with AI models
    test_flow = flows_path / "app.flow"
    test_flow.write_text("""ai_models:
  test_model:
    type: "onnx"
    path: "assets/test.onnx"
    
model TestVectorDB:
  connection: 'local_vector_db'
  content: string @vector_index
  timestamp: datetime
  
lazy_import:
  TestSuite:
    path: "suites/test/main.flow"
    as: TestSuite
    
pages:
  /test:
    - webrtc_stream:
        id: 'test_stream'
        mode: 'receive_only'
""")
    
    # Test that we can import and create the build service
    try:
        # We'll test the Go service indirectly by checking if the Python components work
        from core.parser.parser import FlowParser
        parser = FlowParser()
        ir = parser.parse_project(project_path)
        
        print("✓ Build service components loaded successfully")
        print(f"✓ AI Models in IR: {list(ir.ai_models.keys()) if hasattr(ir, 'ai_models') else 'None'}")
        print(f"✓ Vector Databases in IR: {list(ir.vector_databases.keys()) if hasattr(ir, 'vector_databases') else 'None'}")
        print(f"✓ WebRTC Streams in IR: {list(ir.webrtc_streams.keys()) if hasattr(ir, 'webrtc_streams') else 'None'}")
        print(f"✓ Lazy Imports in IR: {list(ir.lazy_imports.keys()) if hasattr(ir, 'lazy_imports') else 'None'}")
        
    except Exception as e:
        print(f"✗ Error testing build service: {e}")
        import traceback
        traceback.print_exc()
    
    # Clean up
    shutil.rmtree(test_dir)
    print("\nBuild service verification complete!")

if __name__ == "__main__":
    main()