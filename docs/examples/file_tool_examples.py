"""
Example script demonstrating the enhanced FileTool capabilities.

This script shows usage examples for:
1. Pre-validation in edit operations
2. The new patch operation
3. Improved error handling and feedback

NOTE: This is for demonstration purposes and not meant to be executed directly.
You would typically use these operations through the UniversalAgent interface.
"""

import asyncio
import os
from pathlib import Path

# Imports from the Universal Agent framework
from src.universal_agent.tools.file_tool.tool import FileTool
from src.universal_agent.tools.file_tool.operations import FileOperation


async def example_pre_validated_edits():
    """Demonstrates pre-validated edit operations"""
    # Initialize the tool
    file_tool = FileTool(repo_root=".")
    
    # Example file path
    example_file = "example.py"
    
    # Create a sample file
    await file_tool.execute({
        "operation": "write",
        "path": example_file,
        "content": """def example_function():
    return "old_value"

class ExampleClass:
    def method(self):
        return "old_method_value"
"""
    })
    
    print("File created successfully.")
    
    # Example 1: Edit with line-based pre-validation
    # This will succeed because the expected lines match the current content
    result = await file_tool.execute({
        "operation": "edit_lines",
        "path": example_file,
        "start_line": 1,
        "end_line": 2,
        "content": 'def example_function():\n    return "new_value"',
        "expected_lines": ['def example_function():', '    return "old_value"']
    })
    
    print(f"Edit with pre-validation result: {result.success}")
    if result.success:
        print(f"Edit snippet:\n{result.data.get('snippet')}")
    else:
        print(f"Edit error: {result.error}")
    
    # Example 2: Edit that will fail due to content mismatch
    result = await file_tool.execute({
        "operation": "str_replace",
        "path": example_file,
        "old_str": 'return "old_method_value"',
        "new_str": 'return "new_method_value"',
        "expected_content": "This content doesn't match the file"
    })
    
    print(f"\nEdit with invalid pre-validation result: {result.success}")
    if not result.success:
        print(f"Expected validation error: {result.error}")


async def example_patch_operation():
    """Demonstrates the new patch operation"""
    # Initialize the tool
    file_tool = FileTool(repo_root=".")
    
    # Example file path
    example_file = "example_for_patch.py"
    
    # Create a sample file
    await file_tool.execute({
        "operation": "write",
        "path": example_file,
        "content": """def first_function():
    return "unchanged"

def second_function():
    value = "old_value"
    return value

def third_function():
    return "unchanged"
"""
    })
    
    print("\nFile for patching created successfully.")
    
    # Example: Create and apply a patch
    # This is a unified diff format patch
    patch_content = """--- a/example_for_patch.py
+++ b/example_for_patch.py
@@ -4,7 +4,8 @@
 
 def second_function():
-    value = "old_value"
+    # This value has been updated
+    value = "new_value"
     return value
 
 def third_function():
"""
    
    # First validate the patch without applying
    result = await file_tool.execute({
        "operation": "patch",
        "path": example_file,
        "content": patch_content,
        "dry_run": True
    })
    
    print(f"Patch validation result: {result.success}")
    if result.success:
        print(f"Validation message: {result.data.get('message')}")
    
    # Now apply the patch
    result = await file_tool.execute({
        "operation": "patch",
        "path": example_file,
        "content": patch_content,
        "dry_run": False
    })
    
    print(f"\nPatch application result: {result.success}")
    if result.success:
        print(f"Affected lines: {result.data.get('affected_lines')}")
        
    # Read the patched file
    result = await file_tool.execute({
        "operation": "read",
        "path": example_file
    })
    
    if result.success:
        print(f"\nPatched file content:\n{result.data.get('content')}")


async def example_error_handling():
    """Demonstrates the improved error handling"""
    # Initialize the tool
    file_tool = FileTool(repo_root=".")
    
    # Example file path
    example_file = "example_for_errors.py"
    
    # Create a sample file
    await file_tool.execute({
        "operation": "write",
        "path": example_file,
        "content": """def function_with_typo():
    return "example"

# Some comment line
def another_function():
    value = 42
    return value
"""
    })
    
    print("\nFile for error handling created successfully.")
    
    # Example: Attempt a string replacement that will fail
    result = await file_tool.execute({
        "operation": "str_replace",
        "path": example_file,
        "old_str": 'def funktion_with_typo():',  # Misspelled function name
        "new_str": 'def fixed_function():'
    })
    
    print(f"String replacement with typo result: {result.success}")
    if not result.success:
        print(f"Error with closest match suggestion:\n{result.error}")
    
    # Example: Attempt line edit outside valid range
    result = await file_tool.execute({
        "operation": "edit_lines",
        "path": example_file,
        "start_line": 10,  # Beyond end of file
        "end_line": 12,
        "content": "def new_function():\n    return 'new'"
    })
    
    print(f"\nEdit with invalid line range result: {result.success}")
    if not result.success:
        print(f"Line range error: {result.error}")


async def main():
    """Run all examples"""
    await example_pre_validated_edits()
    await example_patch_operation()
    await example_error_handling()
    
    # Clean up example files
    for file in ["example.py", "example_for_patch.py", "example_for_errors.py"]:
        if os.path.exists(file):
            os.remove(file)
    
    print("\nExamples completed and test files cleaned up.")


# Run the examples
if __name__ == "__main__":
    asyncio.run(main())
