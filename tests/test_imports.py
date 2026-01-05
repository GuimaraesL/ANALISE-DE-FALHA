import sys
import os

def test_imports():
    print("Starting import tests...")
    
    modules_to_test = [
        # External dependencies
        "pandas",
        "openpyxl",
        "cv2",
        "streamlit",
        "google.generativeai",
        "agno",
        "google.genai",
        "pdf2image",
        "unidecode",
        "PIL",
        "matplotlib",
        
        # Internal modules
        "core.ai_processor",
        "core.config_loader",
        "core.database",
        "core.excel_reader",
        "core.failure_analysis_app",
        "core.history_manager",
        "core.image_analyzer",
        "core.pdf_as_image_converter",
        "core.prompts",
        "core.report_generator",
        "core.video_analyzer",
        "app",
        "core.agents.analyst_agent",
        "core.agents.tools",
        "ui.styles",
        "ui.texts",
        "ui.utils",
        "config"
    ]
    
    results = []
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"[OK] {module_name}")
            results.append((module_name, True, None))
        except ImportError as e:
            print(f"[FAILED] {module_name}: {e}")
            results.append((module_name, False, str(e)))
        except Exception as e:
            print(f"[ERROR] {module_name}: {e}")
            results.append((module_name, False, str(e)))
            
    print("\nSummary:")
    failed = [m for m, success, err in results if not success]
    if not failed:
        print("All imports successful!")
    else:
        print(f"{len(failed)} imports failed:")
        for m, success, err in results:
            if not success:
                print(f"  - {m}: {err}")

if __name__ == "__main__":
    test_imports()
