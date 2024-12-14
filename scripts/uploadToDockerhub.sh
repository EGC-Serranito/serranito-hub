docker compose -f docker/docker-compose.dev.yml up -d
docker login
docker push meegamagolas/serranito-hub:latest