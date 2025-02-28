from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.user_connections: dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[websocket] = username
        await self.broadcast({"type": "system", "content": f"{username} has joined the chat"})

    def disconnect(self, websocket: WebSocket):
        username = self.user_connections.get(websocket, "Someone")
        self.active_connections.remove(websocket)
        if websocket in self.user_connections:
            del self.user_connections[websocket]
        return username

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket, username)
    try:
        while True:
            data = await websocket.receive_json()
            message = {
                "type": "message",
                "username": username,
                "content": data["message"]
            }
            await manager.broadcast(message)
    except WebSocketDisconnect:
        username = manager.disconnect(websocket)
        await manager.broadcast({"type": "system", "content": f"{username} has left the chat"})