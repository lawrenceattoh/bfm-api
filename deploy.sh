docker buildx build --platform linux/amd64 -t fastapi-backend-neo4j .
docker tag fastapi-backend-neo4j europe-west2-docker.pkg.dev/bfm-sandbox/bfm-services/fastapi-backend-neo4j:latest
docker push europe-west2-docker.pkg.dev/bfm-sandbox/bfm-services/fastapi-backend-neo4j:latest
