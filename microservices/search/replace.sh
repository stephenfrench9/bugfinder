export pod=$(kubectl get pods | grep search | awk '{print $1}')
echo $pod
kubectl delete pod $pod
