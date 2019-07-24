export pod=$(kubectl get pods | grep ios | awk '{print $1}')
echo $pod
kubectl delete pod $pod
