from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OLLAMA_URL = "http://ollama-gpu.ollama.svc.cluster.local:11434/api"
TYPESENSE_URL = "http://typesense.documentresearch.dev:8080"  # Adjust if necessary

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    
    # Search Typesense
    typesense_response = requests.post(f"{TYPESENSE_URL}/collections/shakespeare/documents/search", json={
        "q": query,
        "query_by": "text"
    })
        
    return jsonify({
        "typesense_results": typesense_response.json()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
