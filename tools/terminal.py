import subprocess
import os

MAX_OUTPUT_LENGTH = 4000  # 限制输出字符数，防止撑爆上下文窗口

def execute_bash(command: str, cwd: str = ".", timeout: int = 30) -> str:
    """在指定工作目录运行 bash 命令，支持超时与截断。"""
    try:
        process = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout
        )
        stdout = process.stdout
        stderr = process.stderr
        exit_code = process.returncode

        output = f"[Exit Code: {exit_code}]\n"
        if stdout:
            output += f"[stdout]\n{stdout}\n"
        if stderr:
            output += f"[stderr]\n{stderr}\n"

        if len(output) > MAX_OUTPUT_LENGTH:
            truncated_len = len(output) - MAX_OUTPUT_LENGTH
            output = output[:MAX_OUTPUT_LENGTH] + f"\n... [Output truncated, {truncated_len} characters omitted] ..."

        return output if output.strip() else "[Command produced no output]"

    except subprocess.TimeoutExpired:
        return f"[Error: Command timed out after {timeout} seconds]"
    except Exception as e:
        return f"[Execution Error: {str(e)}]"