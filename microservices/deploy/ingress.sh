export ings=$(kubectl get services -o=jsonpath='{.items['$1'].status.loadBalancer.ingress[*].hostname}')
echo $ings
export names=$(kubectl get services -o=jsonpath='{.items['$1'].metadata.name}')
echo $names
export ports=$(kubectl get services -o=jsonpath='{.items['$1'].spec.ports[0].port}')
echo $ports
echo $ings:$ports

/usr/bin/open -a "/Applications/Google Chrome.app" 'http://'$ings:$ports
