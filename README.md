# kn-ts-01

## ToDo

1. Backend API Development:
   - Create Knative service for the backend API
   - Implement serverless functions for handling search requests
   - Set up error handling and logging

2. Ollama Integration:
  - Configure the backend to communicate with the existing Ollama service
  - Implement API endpoints in the backend to interface with Ollama
  - Ensure proper error handling and timeouts for Ollama requests
  - Optimize performance and manage concurrent requests to Ollama

3. Typesense Setup:
   - ~~Deploy Typesense as a stateful set in Kubernetes~~
   - Create and configure search indexes
   - Implement API for Typesense operations (indexing, searching)

4. Backend-Frontend Integration:
   - Update frontend to make requests to the backend API
   - Implement proper error handling and loading states in the frontend

5. Istio Configuration:
   - Set up Istio gateway and virtual services for routing
   - Configure traffic management between services
   - Implement security policies (mTLS, authorization)

6. Monitoring and Observability:
   - Set up logging aggregation (e.g., Fluentd, Elasticsearch, Kibana)
   - Implement distributed tracing (e.g., Jaeger)
   - Configure metrics collection and dashboards (e.g., Prometheus, Grafana)

7. Testing:
   - Develop unit tests for backend functions
   - Create integration tests for the entire system
   - Perform load testing to ensure scalability

8. CI/CD Pipeline:
   - Set up a CI/CD pipeline for automated testing and deployment
   - Implement canary deployments or blue-green deployments

9. Documentation:
   - Create API documentation
   - Write deployment and operation guides
   - Document system architecture and design decisions

10. Performance Optimization:
    - Analyze and optimize LLM inference performance
    - Fine-tune Typesense for faster search results
    - Optimize Knative autoscaling settings

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
