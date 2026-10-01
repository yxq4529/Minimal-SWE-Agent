import os
from dotenv import load_dotenv
from agent.core import SWEAgent

load_dotenv()

def main():
    # 创建一个隔离的工作区目录防止 Agent 乱改你电脑里的文件
    workspace = "./workspace"
    os.makedirs(workspace, exist_ok=True)
    os.chdir(workspace) # 将执行环境切入 workspace

    # 实例化 Agent，限制最多循环 10 次
    agent = SWEAgent(max_steps=10)
    
    # 给 Agent 下达任务
    task = """
    1. 当前目录下名为 `app.py` 的文件，把 "Hello SWE Agent!" 改成 "Hello V1.0!"
    2. 验证结果正确结束任务。
    """
    
    agent.run(task)

if __name__ == "__main__":
    main()