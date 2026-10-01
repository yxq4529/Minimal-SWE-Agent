import os
from dotenv import load_dotenv
from openai import OpenAI
from tools.terminal import execute_bash

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "execute_bash",
            "description": "Execute a bash command in the workspace directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command line string to run."
                    }
                },
                "required": ["command"]
            }
        }
    }
]

def verify_setup():
    print("1. 测试 Terminal 工具本地执行...")
    local_out = execute_bash("echo 'Terminal tool works!'")
    print(local_out.strip())

    print("\n2. 测试 DeepSeek API 连通与 Tool Calling...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a software engineer agent. Use tools to inspect the environment."},
            {"role": "user", "content": "Check the current directory contents using bash."}
        ],
        tools=tools_schema,
        tool_choice="auto"
    )

    message = response.choices[0].message
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        print(f"成功触发 Tool Call: {tool_call.function.name}")
        print(f"参数: {tool_call.function.arguments}")
    else:
        print("未触发 Tool Call，直接回复:", message.content)

if __name__ == "__main__":
    verify_setup()