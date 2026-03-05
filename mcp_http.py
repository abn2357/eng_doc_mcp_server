from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import os

app = FastAPI()

# --- 配置与工具定义 ---
SERVER_INFO = {
    "name": "java-tron Developer Documentation",
    "version": "1.0.0",
}

# 将工具定义提取出来，以便在 tools/list 中复用
TOOLS_DEFINITION = [
    {
        "name": "SearchJavaTron",
        "description": "Search across the java-tron developer documentation to find node setup and API references.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "A query to search the content with."}
            },
            "required": ["query"]
        }
    }
]

INDEX_PATH = "./site/search/search_index.json"
BASE_URL = "https://abn2357.github.io/documentation-en/"

@app.get("/mcp")
async def get_mcp_config():
    """供浏览器查看的静态配置说明"""
    return {
        "server": SERVER_INFO,
        "capabilities": {"tools": TOOLS_DEFINITION}
    }

@app.post("/mcp")
async def handle_mcp_request(request: Request):
    """核心逻辑：处理 Cursor 的 JSON-RPC 指令"""
    try:
        body = await request.json()
        method = body.get("method")
        request_id = body.get("id")

        # 阶段 1: 握手初始化
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": SERVER_INFO,
                    "capabilities": {
                        "tools": {} # 声明支持工具能力
                    }
                }
            }

        # 阶段 2: 告诉 Cursor 有哪些工具可用 (解决你看到的 No tools 报错)
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": TOOLS_DEFINITION
                }
            }

        # 阶段 3: 处理真正的工具调用执行
        if method == "tools/call":
            params = body.get("params", {})
            if params.get("name") == "SearchJavaTron":
                query = params.get("arguments", {}).get("query", "")
                results = perform_search(query)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": results}]
                    }
                }

        # 阶段 4: 确认初始化完成
        if method == "notifications/initialized":
            return JSONResponse(content={})

        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

def perform_search(query: str):
    """搜索本地索引逻辑"""
    if not os.path.exists(INDEX_PATH):
        return "Error: Index not found. Run 'mkdocs build'."
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    query_lower = query.lower()
    hits = []
    for doc in data['docs']:
        if query_lower in doc['title'].lower() or query_lower in doc['text'].lower():
            hits.append(f"### {doc['title']}\nURL: {BASE_URL}{doc['location']}\nExcerpt: {doc['text'][:200]}...")
            if len(hits) >= 5: break
    return "\n\n".join(hits) if hits else "No relevant documentation found."

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
