import json
import hashlib

with open("C:\\Users\\USER\\Desktop\\moje rzeczy\\projekty\\inne\\TestGenerator\\data\\exported\\e2\\grammar_and_vocabulary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for chunk in data:
    if chunk['section'] == 'vocabulary':
        chunk['id'] = 'vocab-' + hashlib.sha256(chunk['metadata']['content'].encode('utf-8')).hexdigest()[:10]
    else:
        chunk['id'] = 'gram-' + hashlib.sha256(chunk['metadata']['content'].encode('utf-8')).hexdigest()[:10]

with open("C:\\Users\\USER\\Desktop\\moje rzeczy\\projekty\\inne\\TestGenerator\\data\\exported\\e2\\grammar_and_vocabulary.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)