from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import asyncio

# 使用 GPT-4o 作为 LLM 模型
model = ChatOpenAI(
    openai_api_key="xxxxxxxxxxx",
    base_url="https://api.siliconflow.cn/v1",
    model="Qwen/Qwen2.5-7B-Instruct"
)
# 设置服务器参数
server_params = StdioServerParameters(
    command="python",
    args=["mcp_server_easy_rag.py"],
)

# 定义异步任务运行 agent
async def run_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            # 加载工具
            tools = await load_mcp_tools(session)
            # 创建并运行 agent
            agent = create_react_agent(model, tools)
            agent_response = await agent.ainvoke({"messages": "帮我在工具里查一些墙面的注意事项?"})
            return agent_response["messages"][-1].content

# 运行异步函数
if __name__ == "__main__":
    result = asyncio.run(run_agent())
    print(result)