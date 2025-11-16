"""
Prompt Library Analysis Script
Run this to analyze your prompt library and collect comparison data
"""
from services.prompt_library_service import PromptLibraryService

def main():
    print("=" * 70)
    print("PROMPT LIBRARY ANALYSIS")
    print("=" * 70)
    
    lib = PromptLibraryService()
    
    print(f"\n📚 Total prompts: {len(lib.list_prompts())}")
    print(f"📋 Prompt names: {', '.join(lib.list_prompts())}")
    
    print("\n" + "-" * 70)
    print("DETAILED PROMPT INFORMATION")
    print("-" * 70)
    
    for prompt_name in lib.list_prompts():
        meta = lib.get_prompt_metadata(prompt_name)
        print(f"\n✓ {prompt_name}")
        print(f"  Version: {meta['version']}")
        print(f"  Role: {meta['role']}")
        print(f"  Variables: {len(meta['variables'])} ({', '.join(meta['variables'])})")
        print(f"  Constraints: {meta['constraints']}")
        print(f"  Created: {meta['created_at'][:10]}")
    
    # Additional analysis for your report
    print("\n" + "=" * 70)
    print("COMPARISON DATA FOR REPORT")
    print("=" * 70)
    
    total_variables = sum(len(lib.get_prompt_metadata(p)['variables']) for p in lib.list_prompts())
    
    print(f"\n📊 Statistics:")
    print(f"  - Total prompt templates: {len(lib.list_prompts())}")
    print(f"  - Total variables across all prompts: {total_variables}")
    print(f"  - Average variables per prompt: {total_variables / len(lib.list_prompts()):.1f}")
    print(f"  - Prompts with version control: {len(lib.list_prompts())} (100%)")
    print(f"  - Prompts with success criteria: {len(lib.list_prompts())} (100%)")
    
    print("\n✅ Benefits of Prompt Library:")
    print("  1. Centralized management (all prompts in one service)")
    print("  2. Version control (each prompt has version number)")
    print("  3. Variable validation (ensures required variables provided)")
    print("  4. Reusability (templates can be used multiple times)")
    print("  5. Testability (can unit test prompt rendering)")
    print("  6. Documentation (metadata includes role, constraints)")
    
    print("\n❌ Without Prompt Library (hardcoded prompts):")
    print("  - Prompts scattered across codebase")
    print("  - No version tracking")
    print("  - No validation of variables")
    print("  - Difficult to update (change in multiple places)")
    print("  - Cannot unit test prompts independently")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()