docker build -t stephenfrench9/model:prod model
docker push stephenfrench9/model:prod
export pod=$(kubectl get pods | grep model | awk '{print $1}')
echo $pod
kubectl delete pod $pod
