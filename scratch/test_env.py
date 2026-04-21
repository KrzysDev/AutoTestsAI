import os
import dotenv
from pathlib import Path

# Try to find .env in current and parent dirs
dotenv_path = dotenv.find_dotenv()
print(f"Dotenv path found: {dotenv_path}")
dotenv.load_dotenv(dotenv_path)

print(f"CLUSTER_ENDPOINT: {os.getenv('CLUSTER_ENDPOINT')}")
print(f"QDRANT_API_KEY exists: {bool(os.getenv('QDRANT_API_KEY'))}")
