export pod=$(kubectl get pods | grep db | awk '{print $1}')
echo $pod
kubectl delete pod $pod
