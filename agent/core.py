import os
import json
from openai import OpenAI
from agent.prompts import SYSTEM_PROMPT
from tools.terminal import execute_bash
from tools.file_io import read_file, write_file, search_files, patch_file

# 注册大模型可以使用的全部工具 Schema
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "execute_bash",
            "description": "Execute a bash command.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the content of a file.",
            "parameters": {
                "type": "object",
                "properties": {"file_path": {"type": "string"}},
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file. Creates directories if they don't exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Search for files matching a pattern (e.g. '*.py').",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "patch_file",
            "description": "Replace exactly matching 'old_str' with 'new_str' in a file. Use this for minor edits instead of rewriting the whole file. Provide enough context in 'old_str' to ensure it is unique.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "old_str": {"type": "string", "description": "The exact existing text to be replaced."},
                    "new_str": {"type": "string", "description": "The new text."}
                },
                "required": ["file_path", "old_str", "new_str"]
            }
        }
    }
]

# 将字符串映射到实际的 Python 函数
AVAILABLE_TOOLS = {
    "execute_bash": execute_bash,
    "read_file": read_file,
    "write_file": write_file,
    "search_files": search_files,
    "patch_file": patch_file
}

class SWEAgent:
    def __init__(self, max_steps=15):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL")
        )
        self.max_steps = max_steps
        self.model = "deepseek-chat"

    def run(self, task: str):
        # 1. 初始化上下文
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task}
        ]

        print(f"🚀 [Agent Started] Task: {task}\n")

        # 定义最多保留的历史消息条数（一对思考+工具调用通常算 2-3 条）
        MAX_HISTORY = 12

        # 2. 开启核心 Loop
        for step in range(self.max_steps):
            print(f"--- Step {step + 1} ---")

            # 👇 新增：上下文截断（滑动窗口）逻辑
            if len(messages) > MAX_HISTORY + 2:  # +2 是保留 system prompt 和 initial user task
                print("🧹 [Context Manager]: Truncating old history to save tokens...")
                # 永远保留前两项 [0:2]，截取最后 MAX_HISTORY 项 [-MAX_HISTORY:]
                messages = messages[:2] + messages[-MAX_HISTORY:]

            # 确保截断后，第一条被保留的历史记录不是 "tool" 角色（OpenAI 规范要求 tool 必须跟在 tool_calls 后面）
            while len(messages) > 2 and messages[2]["role"] == "tool":
                messages.pop(2)
            
            # 请求大模型
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto"
            )

            msg = response.choices[0].message
            # 将模型的回复原封不动塞回上下文 (排除 None 值防止 API 报错)
            messages.append(msg.model_dump(exclude_none=True))

            # 打印模型的思考过程或普通回复
            if msg.content:
                print(f"🤖 [Agent Thoughts]:\n{msg.content}")
                
                # 3. 终止条件检查
                if "[TASK_COMPLETED]" in msg.content:
                    print("\n✅ Task successfully completed!")
                    return

            # 4. 执行 Tool Call (如果有)
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    func_name = tool_call.function.name
                    try:
                        args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                        
                    print(f"🛠️  [Action]: Calling `{func_name}` with {args}")

                    # 路由到对应的本地函数
                    if func_name in AVAILABLE_TOOLS:
                        try:
                            result = AVAILABLE_TOOLS[func_name](**args)
                        except Exception as e:
                            result = f"[Error executing tool]: {str(e)}"
                    else:
                        result = f"[Error]: Tool {func_name} not found."

                    print(f"📄 [Result]:\n{str(result)[:300]}...\n") # 仅打印前300字防刷屏

                    # 5. 将执行结果作为 'tool' 角色拼接入上下文
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": str(result)
                    })
            else:
                # 既没调用工具，也没输出完成标志，属于模型发呆，强制推一把
                if "[TASK_COMPLETED]" not in (msg.content or ""):
                    print("⚠️ [Warning]: No actions taken. Forcing next step...")
                    messages.append({
                        "role": "user", 
                        "content": "Please continue to use tools to complete the task, or output [TASK_COMPLETED] if you are done."
                    })

        # 超过最大循环次数
        print("\n❌ Max steps reached. Task aborted to prevent infinite loop.")