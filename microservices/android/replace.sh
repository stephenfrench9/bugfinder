export pod=$(kubectl get pods | grep android | awk '{print $1}')
echo $pod
kubectl delete pod $pod
