docker run --name app-search -d search
docker network create my-net
docker network connect my-net app-search
