# coding: UTF-8
import asyncio
import websockets
import requests


async def handler(websocket):
    while True:
        data = await websocket.recv()
        
        async def send_inference_request(data):
            url = 'http://localhost:1234/v1/completions'
            headers = {'Content-Type': 'application/json'}
            payload = {
                'prompt': "次の、絶滅危惧種のレッドリストに関する質問に答えて。簡単に簡潔に答えて。質問に対する回答以外は書かないで。＃＃＃質問："+data+"＃＃＃回答：",
                'temperature': 0.7,
                'max_tokens': 100
            }

            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                generated_text = response.json()["choices"][0]["text"]
                await websocket.send(generated_text)
                return generated_text
            else:
                print("エラーが発生しました:", response.status_code, response.text)
                return None
    
        await send_inference_request(data)
    
async def main():
    async with websockets.serve(handler, "localhost", 8000):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())