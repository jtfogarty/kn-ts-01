```bash
kubectl create configmap ts-kn-srch-configmap 
         --from-file=Dockerfile=./Dockerfile 
         --from-file=nginx.conf=./nginx.conf
         --from-file=search.html=./search.htmx