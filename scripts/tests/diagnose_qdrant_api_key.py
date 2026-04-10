import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

url = os.getenv("CLUSTER_ENDPOINT")
key = os.getenv("QDRANT_API_KEY")

print(f"URL: {url}")
print(f"Key: {'SET' if key else 'MISSING'}")