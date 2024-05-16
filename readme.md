# Kubernetes scraper

Project for scraping webpages using kubernetes.x

Starting the project:
````ps
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
````

Expose Kibana on Windows:

````ps
kubectl describe services/kibana
````