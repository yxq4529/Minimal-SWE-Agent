import os
import glob

def read_file(file_path: str, cwd: str = ".") -> str:
    full_path = os.path.join(cwd, file_path)
    if not os.path.exists(full_path):
        return f"[Error: File '{file_path}' does not exist]"
    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"[Error reading file: {str(e)}]"

def write_file(file_path: str, content: str, cwd: str = ".") -> str:
    full_path = os.path.join(cwd, file_path)
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"[Success: File '{file_path}' written successfully]"
    except Exception as e:
        return f"[Error writing file: {str(e)}]"

def search_files(pattern: str, cwd: str = ".") -> str:
    search_path = os.path.join(cwd, "**", pattern)
    matches = glob.glob(search_path, recursive=True)
    relative_matches = [os.path.relpath(p, cwd) for p in matches]
    if not relative_matches:
        return "[No matching files found]"
    return "\n".join(relative_matches[:50])
# 基于字符串匹配或行号替换的 patch_file 工具。
def patch_file(file_path: str, old_str: str, new_str: str, cwd: str = ".") -> str:
    """
    在文件中查找完全匹配的 old_str，并替换为 new_str。
    """
    full_path = os.path.join(cwd, file_path)
    if not os.path.exists(full_path):
        return f"[Error: File '{file_path}' does not exist]"
    
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # 检查 old_str 是否存在，且必须唯一（防止误替换）
        count = content.count(old_str)
        if count == 0:
            return "[Error: `old_str` not found in file. Make sure you provided the exact text.]"
        elif count > 1:
            return f"[Error: `old_str` found {count} times. Please provide a more unique context string to replace.]"
            
        new_content = content.replace(old_str, new_str)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        return f"[Success: File '{file_path}' patched successfully.]"
        
    except Exception as e:
        return f"[Error patching file: {str(e)}]"