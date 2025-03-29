from fastapi import APIRouter, WebSocket
import json
router = APIRouter()
connected_websockets={}
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print('ws')
    await websocket.accept()
    async for message in websocket.iter_text():
        print(message)
        message_dict = json.loads(message)
        print(message_dict)
        if 'action' in message_dict:
            if message_dict['action'] == 'login':
                websocket.app.connected_websockets[message_dict['user_id']] = websocket
                print(websocket.app.connected_websockets)