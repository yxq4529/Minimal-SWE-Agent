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

    # docs/demo1.png # 给 Agent 下达任务 
    # task = """
    # 1. 请帮我写一个 Python 脚本，名为 `calculator.py`。
    # 2. 这个脚本里需要包含一个计算斐波那契数列第 n 项的函数 `fib(n)`，并打印出 fib(10) 的结果。
    # 3. 写完之后，请用终端执行一下这个脚本，确保它能正常运行并且结果正确。
    # """

    # docs/demo2.png
    # task = """
    # 1. 在当前目录下创建一个名为 `app.py` 的文件，写一个使用 Flask 框架的最简单的 Web 服务，监听 5001 端口，访问根路径返回 'Hello SWE Agent!'。
    # 2. 如果当前环境没有安装 flask，请使用 execute_bash 执行 `pip install flask` 安装它。
    # 3. 安装完成后，使用 execute_bash 在后台启动 `app.py` (提示: 可以用 python app.py &)。
    # 4. 启动后，使用 execute_bash 运行 `curl http://127.0.0.1:5001` 来验证服务是否正常返回了文字。
    # 5. 验证成功后结束任务。
    # """
    
    # docs/demo3.png
    # 给 Agent 下达任务
    task = """
    1. 当前目录下名为 `app.py` 的文件，把 "Hello SWE Agent!" 改成 "Hello V1.0!"
    2. 验证结果正确结束任务。
    """
    
    agent.run(task)

if __name__ == "__main__":
    main()