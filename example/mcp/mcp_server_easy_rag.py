from mcp.server.fastmcp import FastMCP
import httpx
# Initialize FastMCP server
mcp = FastMCP("easy_rag")

@mcp.tool()
async def get_todos(keyword: str) -> str:
    """Search for content from the Rag knowledge base
    Args:
        keyword:What you want to search for
    """
    url = "http://127.0.0.1:8903/api/search"
    data = {
        "q": keyword,
        "agent_id": 0,
        "scene_id": 0,
        "file_id": 0
    }
    headers = {"Content-Type": "application/json"}
    client = httpx.Client()
    try:
        # 发送 POST 请求
        response = client.post(url, json=data, headers=headers)
        # 检查响应状态码
        if response.status_code == 200:
            print("请求成功！")
            # 解析 JSON 响应
            response_data = response.json()
            # 提取 data 字段下的列表
            data_list = response_data.get("data", [])
            # 提取每个 content 的值并拼接成一个字符串
            content_string = "".join(item.get("content", "") for item in data_list)
            print("拼接后的字符串:", content_string)
            return content_string
        else:
            print(f"请求失败，状态码：{response.status_code}")
            print("响应内容：", response.text)
    except Exception as e:
        print(f"请求过程中发生错误：{e}")
    finally:
        # 关闭客户端
        client.close()
def run_server():
    mcp.run(transport='stdio')
if __name__ == "__main__":
    # Initialize and run the server
    run_server()