import httpx
import json
import asyncio

# 配置测试目标
TARGET_URL = "http://localhost:8001/mcp"

async def test_mcp_server():
    async with httpx.AsyncClient() as client:
        print("=== 阶段 1: 测试 GET 请求 (获取能力说明书) ===")
        # 模拟 Cursor 初始化或用户访问配置页
        response_get = await client.get(TARGET_URL)
        if response_get.status_code == 200:
            print("✅ GET 成功!")
            print(json.dumps(response_get.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ GET 失败: {response_get.status_code}")

        print("\n" + "="*50 + "\n")

        print("=== 阶段 2: 测试 POST 请求 (模拟 Cursor 工具调用) ===")
        # 构造符合 MCP 规范的 JSON-RPC 请求体
        # 模拟用户提问关于“私有网 (private network)”的问题
        payload = {
            "jsonrpc": "2.0",
            "id": "cursor-test-id-001",
            "method": "tools/call",
            "params": {
                "name": "SearchJavaTron",
                "arguments": {
                    "query": "private network"
                }
            }
        }

        response_post = await client.post(
            TARGET_URL, 
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response_post.status_code == 200:
            result = response_post.json()
            print("✅ POST 成功!")
            # 提取并打印 AI 将会看到的文档片段
            content = result.get("result", {}).get("content", [{}])[0].get("text", "")
            print("返回的文档片段:")
            print("-" * 30)
            print(content)
            print("-" * 30)
        else:
            print(f"❌ POST 失败: {response_post.status_code}")
            print(response_post.text)

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
