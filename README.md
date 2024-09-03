# kn-ts-01

This project is a proof of concept for using Typesense as the backend for a search service. It is built with Knative, htmx, and Typesense.

The components are:

- **search-frontend**: A simple frontend built with htmx.
- **search-middle**: A simple backend built with Knative.
- **search-typesense**: The search backend.

## Completed Tasks

- Setup Knative
   - running and good to go
- Setup Typesense
   - added Shakespear to Typesense
   - tested pulling data from Typesense
- setup frontend
   - created htmx file
   - created Dockerfile
   - used kaniko to build and push to registry

## Tasks remaining
- create Knative Service for the backend API
- istio integration for this knative service

## KNative Backend

1. Use the internal Ollama URL in your backend configuration:
   ```
   OLLAMA_URL=http://ollama-gpu.ollama.svc.cluster.local:11434/api
   ```

2. Implement functions in your backend service to send requests to this Ollama endpoint. For example:

   ```python
   import requests

   OLLAMA_URL = "http://ollama-gpu.ollama.svc.cluster.local:11434/api"

   def query_ollama(prompt):
       response = requests.post(f"{OLLAMA_URL}/generate", json={
           "model": "llama2:13b",
           "prompt": prompt
       })
       if response.status_code == 200:
           return response.json()['response']
       else:
           raise Exception(f"Ollama request failed: {response.status_code}")
   ```

3. Ensure your backend service has the necessary network policies to communicate with the Ollama service within the cluster.

4. Implement appropriate error handling, retries, and timeouts for requests to Ollama.

5. Consider implementing a caching layer if you expect repeated similar queries to reduce load on the Ollama service.

6. Monitor the performance and resource usage of your Ollama service, and adjust your backend's concurrency and rate limiting as needed to prevent overload.

The below is how to create the configmap when using kaniko to create the image.

### knative configmap
```bash
kubectl create configmap ts-kn-mid-configmap \
       --from-file=Dockerfile=./Dockerfile \
       --from-file=requirements.txt=./requirements.txt \
       --from-file=search.py=./search.py
```