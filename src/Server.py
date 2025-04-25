from fastapi import FastAPI,BackgroundTasks,WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.Agents import AgentClass
import uvicorn
from openai import RateLimitError
import uuid
import asyncio
from src.AddDoc import AddDocClass



app = FastAPI()
# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.post("/chat")
def SyncChat(query: str,background_tasks: BackgroundTasks):
    agent = AgentClass()
    msg = agent.run_agent(query)
    unique_id = str(uuid.uuid4()) 
    return {"msg": msg, "id": unique_id}

# 心跳检测
async def send_heartbeat(websocket: WebSocket):
    while True:
        try:
            await websocket.send_text("Ping")
            await asyncio.sleep(2)
        except Exception as e:
            print("心跳发送失败", e)
            break

@app.post("/add_urls")
async def add_urls(urls: str):
    add_doc = AddDocClass()
    await add_doc.add_urls(urls)

@app.post("/add_pdfs")
def add_pdfs(files: str):
    pass
@app.post("/add_txts")
def add_txts(files: str):
    pass
@app.post("/add_youtubes")
def add_youtubes(files: str):
    pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connection_closed = False
    asyncio.ensure_future(send_heartbeat(websocket))
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "Pong":
                print("Pong")
            else:

                try:
                    agent = AgentClass()
                    async for chunk in agent.run_agent_ws(data):
                        await websocket.send_text(chunk)

                except RateLimitError:
                        await websocket.send_text("Rate Limit Error")
                        connection_closed = True
                        break
                except Exception as e:
                    print("An error occurred:", e)
                    connection_closed = True
                    break

                if not connection_closed:
                    await websocket.send_text("##END##")
    except WebSocketDisconnect:
        print("WebSocket connection closed")
        connection_closed = True
    finally:
        if not connection_closed:
            await websocket.close()
        print("WebSocket connection closed")


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)