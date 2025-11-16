"""
Setup Verification Script
Run this to verify your installation is correct before executing experiments
"""
import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("Checking Python version...", end=" ")
    if sys.version_info >= (3, 10):
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
        return True
    else:
        print(f"✗ Python {sys.version_info.major}.{sys.version_info.minor} (need 3.10+)")
        return False


def check_dependencies():
    """Check required packages"""
    print("\nChecking dependencies...")
    required = [
        'openai',
        'pytest',
        'pydantic',
        'yaml',
        'aiohttp'
    ]
    
    missing = []
    for package in required:
        try:
            if package == 'yaml':
                __import__('yaml')
            else:
                __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    return True


def check_files():
    """Check required files exist"""
    print("\nChecking project files...")
    required_files = [
        'config.yaml',
        'main.py',
        'experiment_runner.py',
        'requirements.txt',
        'services/prompt_library_service.py',
        'services/agent_orchestration_service.py',
        'services/evaluation_service.py',
        'services/logging_service.py',
        'tests/test_prompt_library.py',
        'tests/test_evaluation.py',
        'tests/test_integration.py'
    ]
    
    missing = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path}")
            missing.append(file_path)
    
    if missing:
        print(f"\n❌ Missing files: {', '.join(missing)}")
        return False
    return True


def check_api_key():
    """Check if API key is configured"""
    print("\nChecking API key configuration...")
    
    # Check environment variable
    env_key = os.getenv('OPENAI_API_KEY')
    if env_key and env_key != 'YOUR_API_KEY_HERE':
        print("  ✓ API key found in environment variable")
        return True
    
    # Check main.py
    try:
        with open('main.py', 'r') as f:
            content = f.read()
            if 'YOUR_API_KEY_HERE' not in content or 'sk-' in content:
                print("  ✓ API key configured in main.py")
                return True
    except Exception:
        pass
    
    print("  ⚠ API key not configured")
    print("    Please set OPENAI_API_KEY environment variable")
    print("    OR edit main.py and experiment_runner.py")
    return False


def check_directories():
    """Check/create required directories"""
    print("\nChecking directories...")
    dirs = ['logs', 'experiment_results', 'services', 'tests']
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            print(f"  ⚠ Creating {dir_name}/")
            dir_path.mkdir(exist_ok=True)
        else:
            print(f"  ✓ {dir_name}/")
    return True


def run_basic_test():
    """Run a basic import test"""
    print("\nRunning basic functionality test...")
    try:
        from services.prompt_library_service import PromptLibraryService
        service = PromptLibraryService()
        prompts = service.list_prompts()
        print(f"  ✓ Loaded {len(prompts)} prompt templates")
        
        from services.evaluation_service import EvaluationService
        eval_service = EvaluationService({'requirements': {'non_functional': {}}})
        print(f"  ✓ Evaluation service initialized")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Run all verification checks"""
    print("="*70)
    print("Multi-Agent System Setup Verification")
    print("="*70)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Files", check_files),
        ("Directories", check_directories),
        ("Basic Functionality", run_basic_test),
        ("API Key", check_api_key)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "="*70)
    print("Verification Summary")
    print("="*70)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {name}")
    
    all_passed = all(result for _, result in results[:-1])  # Exclude API key check
    api_key_configured = results[-1][1]
    
    print("\n" + "="*70)
    if all_passed and api_key_configured:
        print("✅ All checks passed! You're ready to run experiments.")
        print("\nNext steps:")
        print("  python main.py              # Run basic examples")
        print("  python experiment_runner.py # Run full experiments")
        print("  pytest tests/ -v            # Run test suite")
    elif all_passed:
        print("⚠️  Setup is good, but API key not configured.")
        print("\nTo configure API key:")
        print("  export OPENAI_API_KEY='sk-...'  # Set environment variable")
        print("  OR edit main.py and replace YOUR_API_KEY_HERE")
        print("\nYou can run unit tests without API key:")
        print("  pytest tests/test_prompt_library.py -v")
        print("  pytest tests/test_evaluation.py -v")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    print("="*70)


if __name__ == "__main__":
    main()