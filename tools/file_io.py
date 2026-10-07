import os
import glob

def read_file(file_path: str, cwd: str = ".") -> str:
    """读取文件内容。包含大文件截断保护机制。"""
    full_path = os.path.join(cwd, file_path)
    if not os.path.exists(full_path):
        return f"[Error: File '{file_path}' does not exist]"
        
    try:
        # 使用 errors="replace" 防止遇到非 utf-8 编码文件（如图片/二进制的误读）报错
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            
        MAX_LINES = 500
        
        if len(lines) > MAX_LINES:
            truncated_content = "".join(lines[:MAX_LINES])
            warning_msg = (
                f"\n\n... [Warning: File truncated. The file has {len(lines)} lines, "
                f"but only the first {MAX_LINES} are shown to prevent context overflow. "
                f"Please use `execute_bash` with `grep -n <keyword>` or `sed -n '<start>,<end>p'` "
                f"to inspect specific sections.]"
            )
            return truncated_content + warning_msg
            
        return "".join(lines)
        
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