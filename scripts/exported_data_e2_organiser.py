import json

with open("C:\\Users\\USER\\Desktop\\moje rzeczy\\projekty\\inne\\TestGenerator\\data\\exported\\e2\\grammar_and_vocabulary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

vocab_chunks = []
grammar_chunks = []

for chunk in data:
    if chunk['section'] == 'vocabulary':
        vocab_chunks.append(chunk)
    else:
        grammar_chunks.append(chunk)

with open("C:\\Users\\USER\\Desktop\\moje rzeczy\\projekty\\inne\\TestGenerator\\data\\v2\\vocabulary.json", "w", encoding="utf-8") as f:
    json.dump(vocab_chunks, f, indent=2)

with open("C:\\Users\\USER\\Desktop\\moje rzeczy\\projekty\\inne\\TestGenerator\\data\\v2\\grammar.json", "w", encoding="utf-8") as f:
    json.dump(grammar_chunks, f, indent=2)