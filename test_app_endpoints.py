from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

# 1. Test index
r = client.get('/')
assert r.status_code == 200, f'Index failed: {r.status_code}'
assert 'GraphRAG Literature Platform' in r.text, 'Title not in HTML'
print('Test 1: Index HTML served successfully.')

# 2. Test /api/stats
r = client.get('/api/stats')
assert r.status_code == 200, f'Stats failed: {r.status_code}'
data = r.json()
print(f"Test 2: Stats returned: {data['total_articles']} articles, {data['total_nodes']} nodes, {data['total_edges']} edges.")

# 3. Test /api/articles
r = client.get('/api/articles')
assert r.status_code == 200
arts = r.json()['articles']
print(f"Test 3: Articles count = {len(arts)}")

# 4. Test /api/pico
r = client.get('/api/pico')
assert r.status_code == 200
pico_rows = r.json()['pico_rows']
print(f"Test 4: PICO rows count = {len(pico_rows)}")

# 5. Test /api/ner
r = client.get('/api/ner')
assert r.status_code == 200
ents = r.json()['entities']
print(f"Test 5: NER entities count = {len(ents)}")

# 6. Test /api/graph
r = client.get('/api/graph')
assert r.status_code == 200
g = r.json()
print(f"Test 6: Graph nodes = {len(g['nodes'])}, edges = {len(g['edges'])}")

# 7. Test /api/chat
r = client.post('/api/chat', json={'query': 'Which SGLT2 inhibitor trials reported kidney disease progression in CKD?'})
assert r.status_code == 200
chat_res = r.json()
print(f"Test 7: Chat response intent = {chat_res['intent']}, audit = {chat_res['audit']['status_badge']}")

print('=== ALL 7 SYSTEM TESTS PASSED PERFECTLY ===')
