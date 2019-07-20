#!/usr/bin/env bash
kubectl create namespace observability
kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/crds/jaegertracing_v1_jaeger_crd.yaml
kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/service_account.yaml
kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/role.yaml
kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/role_binding.yaml
kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/operator.yaml
kubectl apply -f elasticsearch.yml
kubectl apply -f simple-prod.yaml #  you must run this command from /jaeger, not /.
# make an instance of jaeger
#kubectl apply -f simple-prod-deploy-es.yaml
# look at ingress
kubectl get ingress
# look at services
kubectl get services
# make that service public
# sleep 3			       
# kubectl edit service simple-prod-query
