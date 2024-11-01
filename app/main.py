import uvicorn

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.api.v1 import api_router
from app.core import settings

from app.api.v1.arenas import Simple

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    Simple.active_connections[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            await Simple.send_msg(user_id, f"Echo: {data}")  # Echo back to the user
    except WebSocketDisconnect:
        del Simple.active_connections[user_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
