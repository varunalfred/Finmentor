import asyncio
import aiohttp
import json
import os

# Set dummy API key for testing if not present
if "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = "dummy_key"

async def test_streaming_chat():
    url = "http://localhost:8000/api/chat"
    payload = {
        "message": "Explain the concept of compound interest",
        "input_type": "text",
        "user_profile": {
            "user_id": "test_user",
            "education_level": "beginner"
        }
    }

    print(f"Connecting to {url}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    print(f"Error: {response.status}")
                    print(await response.text())
                    return

                print("Connected! Receiving stream...")
                
                buffer = ""
                async for chunk in response.content.iter_any():
                    text = chunk.decode('utf-8')
                    buffer += text
                    
                    # Process lines
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if data['type'] == 'thought':
                                    print(f"💭 THOUGHT: {data['content']}")
                                elif data['type'] == 'token':
                                    print(f"{data['content']}", end="", flush=True)
                                elif data['type'] == 'error':
                                    print(f"\n❌ ERROR: {data['content']}")
                                elif data['type'] == 'metadata':
                                    print(f"\n💾 METADATA: {data['content']}")
                            except json.JSONDecodeError:
                                print(f"\n⚠️ Parse Error: {line}")
                                
                print("\n\nStream finished.")
                
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_streaming_chat())
