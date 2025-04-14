# FileTool Enhancements

This document describes the enhancements made to the `FileTool` to improve robustness, reliability, and user experience when editing files.

## Overview of Enhancements

The `FileTool` now includes these key improvements:

1. **Pre-validation for Edits**
   - Verify the expected file state before applying changes
   - Prevent edits to files that have changed since they were last read
   - Provide detailed context when validation fails

2. **Improved Error Messages**
   - Include line numbers, expected vs. actual content
   - Show context around areas where text doesn't match
   - Suggest closest matches for text that can't be found

3. **New Patch Operation**
   - Apply changes using standard unified diff/patch format
   - Validate patch context before applying changes
   - Support targeted edits without needing the entire file content

## Using Pre-validation

The edit handlers now support pre-validation to ensure changes are applied to the expected file content:

### Line-based Edits

```python
# Replace lines only if they match expected_lines
await handle_edit_lines(
    create_result_method,
    repo_root,
    file_path,
    start_line,
    end_line,
    new_content,
    file_history,
    snippet_lines=4,
    expected_lines=["def old_function():", "    return 'old'"]
)
```

### String Replacements

```python
# Replace string only if the file hasn't changed since expected_content
await handle_str_replace(
    create_result_method,
    repo_root,
    file_path,
    old_str,
    new_str,
    file_history,
    snippet_lines=4,
    expected_content="Original file content..."
)
```

### Insertions

```python
# Insert at line only if the context line matches
await handle_insert(
    create_result_method,
    repo_root,
    file_path,
    insert_line,
    content,
    file_history,
    snippet_lines=4,
    context_line="def function_before_insertion():"
)
```

## Using the Patch Operation

The new patch operation allows applying targeted changes using standard unified diff format:

```python
# Create a unified diff
patch_content = """
--- a/file.py
+++ b/file.py
@@ -10,7 +10,7 @@
 def example():
-    return 'old'
+    return 'new'
 
"""

# Apply the patch
await handle_patch(
    create_result_method,
    repo_root,
    file_path,
    patch_content,
    dry_run=False,  # Set to True to validate without applying
    file_history
)
```

## Advanced Error Handling

If validation fails, the error messages now provide much more context:

```
Pre-validation failed: Lines 10-12 do not match expected content:
10:     def example():
11: (−) return 'old'
    : (+) return 'old_modified'
```

In the case of text not found, the closest match will be suggested:

```
Pre-validation failed: Expected text not found in 'file.py'
Closest match at line 15:
Expected: def old_function():
Found:    def old_function_renamed():
```

## Implementation Details

These enhancements were implemented in an organized, modular way:

1. **New Utility Functions**:
   - `verify_lines_context()` - Verify line-based content matches expectations
   - `verify_text_context()` - Verify text exists in a file
   - `format_diff_with_context()` - Format human-readable diffs
   - `find_closest_match()` - Find similar text when exact matches fail
   - `parse_patch()` - Parse unified diff format
   - `apply_patch()` - Apply parsed patch with validation

2. **New Handler Module**:
   - `patch_handlers.py` - Implements the new patch operation

3. **Enhanced Edit Handlers**:
   - All edit handlers now support pre-validation parameters
   - Error messages include detailed context information

These enhancements make the file editing tools more robust against changes occurring in files between reads and edits, providing better guardrails against unintended modifications.
