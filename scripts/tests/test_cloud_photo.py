from backend.app.services.ai_service import AiService
import time

def main():
    service = AiService()

    photo_path = r"C:\Users\USER\Desktop\Ai Test Generator Dataset-20260321T142317Z-1-001\Ai Test Generator Dataset\2.jpg"

    with open(photo_path, "rb") as f:
        photo_data = f.read()

    print(f"Image size: {len(photo_data)} bytes")
    print("Sending request WITHOUT streaming...")

    start = time.time()
    try:
        response = service.cloud_client.chat(
            'qwen3-vl:235b-cloud',
            messages=[{
                'role': 'user',
                'content': 'Describe this image in one sentence.',
                'images': [photo_data],
            }],
            stream=False
        )
        elapsed = time.time() - start
        print(f"Response received in {elapsed:.1f}s")
        print(response['message']['content'])
    except Exception as e:
        elapsed = time.time() - start
        print(f"ERROR after {elapsed:.1f}s: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
