docker run --name app-ios -d front
docker network create my-net
docker network connect my-net app-ios
