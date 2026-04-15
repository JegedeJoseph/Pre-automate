#!/usr/bin/env python3
"""
validate.py - Verify all components are in place and working
Run: python validate.py
"""

import os
import sys
import importlib.util
from pathlib import Path

def check_file(filepath, description):
    """Check if file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND: {filepath}")
        return False

def check_import(module_name, description):
    """Check if Python module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {description}")
        return True
    except ImportError as e:
        print(f"❌ {description} - IMPORT ERROR: {e}")
        return False

def check_env():
    """Check if environment variables are set."""
    required_vars = [
        'GOOGLE_CREDENTIALS_JSON',
        'YOUR_GMAIL',
        'GMAIL_APP_PASSWORD',
        'ANTHROPIC_API_KEY',
        'APPLICANT_NAME',
        'APPLICANT_EMAIL'
    ]
    
    print("\n📋 Environment Variables:")
    all_set = True
    for var in required_vars:
        if os.environ.get(var):
            print(f"✅ {var}")
        else:
            print(f"❌ {var} - NOT SET")
            all_set = False
    
    return all_set

def validate():
    """Run all validations."""
    print("=" * 60)
    print("🔍 JOB AUTOMATION BOT - VALIDATION")
    print("=" * 60)
    
    checks = {
        "📁 Project Files": [
            ("main.py", "Main pipeline"),
            ("scraper.py", "Job scrapers"),
            ("applier.py", "Auto-apply handlers"),
            ("scorer.py", "Job scoring"),
            ("cover_letter.py", "Cover letter generator"),
            ("sheets_logger.py", "Google Sheets logger"),
            (".env.example", ".env template"),
            ("requirements.txt", "Python dependencies"),
            ("README.md", "Setup guide"),
            ("IMPLEMENTATION.md", "Implementation checklist"),
            ("QUICKSTART.md", "Quick reference"),
            (".github/workflows/run_daily.yml", "GitHub Actions workflow"),
        ],
        "🐍 Python Packages": [
            ("playwright", "Playwright browser automation"),
            ("gspread", "Google Sheets API client"),
            ("httpx", "Async HTTP client"),
            ("google", "Google Cloud libraries"),
        ],
        "🔗 Python Modules": [
            ("scraper", "Scraper module"),
            ("applier", "Applier module"),
            ("scorer", "Scorer module"),
            ("cover_letter", "Cover letter module"),
            ("sheets_logger", "Sheets logger module"),
        ]
    }
    
    results = {}
    
    # Check project files
    print("\n📁 Project Files:")
    results["files"] = all([
        check_file(filepath, desc) 
        for filepath, desc in checks["📁 Project Files"]
    ])
    
    # Check Python packages
    print("\n🐍 Python Packages:")
    results["packages"] = all([
        check_import(pkg, desc) 
        for pkg, desc in checks["🐍 Python Packages"]
    ])
    
    # Check Python modules
    print("\n🔗 Python Modules:")
    results["modules"] = all([
        check_import(mod, desc) 
        for mod, desc in checks["🔗 Python Modules"]
    ])
    
    # Check environment
    print("\n" + "=" * 60)
    env_ok = check_env()
    results["env"] = env_ok
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    if results["files"]:
        print("✅ All project files present")
    else:
        print("❌ Missing project files - clone repo or check directory")
    
    if results["packages"]:
        print("✅ All Python packages installed")
    else:
        print("❌ Missing packages - run: pip install -r requirements.txt")
    
    if results["modules"]:
        print("✅ All modules importable")
    else:
        print("❌ Module import errors - check installation")
    
    if env_ok:
        print("✅ All environment variables set")
    else:
        print("❌ Missing env vars - create .env file from .env.example")
    
    print("\n" + "=" * 60)
    
    if all(results.values()):
        print("🎉 ALL CHECKS PASSED - READY TO RUN!")
        print("   Command: python main.py")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED - FIX ABOVE ISSUES")
        print("   See README.md and IMPLEMENTATION.md for help")
        return 1

if __name__ == "__main__":
    exit_code = validate()
    sys.exit(exit_code)
