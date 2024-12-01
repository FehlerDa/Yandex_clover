from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/alice")
async def handle_alice_command(request: Request):
    data = await request.json()

    command = data['request']['command'].lower()

    response_text = "Команда не распознана."

    if "безопасность" in command:
        print('Защита включена')
        response_text = "Защита включена."

    
    return {
        "response": {
            "text": response_text,
            "end_session": False
        },
        "version": "1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)