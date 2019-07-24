export pod=$(kubectl get pods | grep model | awk '{print $1}')
echo $pod
kubectl delete pod $pod
