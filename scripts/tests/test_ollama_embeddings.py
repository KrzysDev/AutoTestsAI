import ollama

response = ollama.embed(
    model='qwen3-embedding:0.6b',
    input='The sky is blue because of Rayleigh scattering',
)
print(len(response.embeddings))

