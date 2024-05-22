#!/bin/bash

# Wait for Elasticsearch to start up
until curl -u "elastic:${ELASTIC_PASSWORD}" -s http://elasticsearch:9200/_cluster/health | grep -q '"status":"green"\|"status":"yellow"'; do
  echo "Waiting for Elasticsearch to be ready..."
  sleep 5
done

# Create the kibana_system user
curl -u "elastic:${ELASTIC_PASSWORD}" -X POST "http://elasticsearch:9200/_security/user/kibana_system" -H "Content-Type: application/json" -d '{
  "password" : "'"${KIBANA_PASSWORD}"'",
  "roles" : [ "kibana_system" ],
  "full_name" : "Kibana System User"
}'
