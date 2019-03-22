Organizing resource configurations
Many applications require multiple resources to be created, such as a Deployment and a Service. Management of multiple resources can be simplified by grouping them together in the same file (separated by --- in YAML). For example:

application/nginx-app.yaml Copy application/nginx-app.yaml to clipboard
apiVersion: v1
kind: Service
metadata:
  name: my-nginx-svc
  labels:
    app: nginx
spec:
  type: LoadBalancer
  ports:
  - port: 80
  selector:
    app: nginx
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-nginx
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.7.9
        ports:
        - containerPort: 80
Multiple resources can be created the same way as a single resource:

kubectl create -f https://k8s.io/examples/application/nginx-app.yaml
service/my-nginx-svc created
deployment.apps/my-nginx created
The resources will be created in the order they appear in the file. Therefore, it’s best to specify the service first, since that will ensure the scheduler can spread the pods associated with the service as they are created by the controller(s), such as Deployment.

kubectl create also accepts multiple -f arguments:

kubectl create -f https://k8s.io/examples/application/nginx/nginx-svc.yaml -f https://k8s.io/examples/application/nginx/nginx-deployment.yaml
And a directory can be specified rather than or in addition to individual files:

kubectl create -f https://k8s.io/examples/application/nginx/
kubectl will read any files with suffixes .yaml, .yml, or .json.

It is a recommended practice to put resources related to the same microservice or application tier into the same file, and to group all of the files associated with your application in the same directory. If the tiers of your application bind to each other using DNS, then you can then simply deploy all of the components of your stack en masse.

A URL can also be specified as a configuration source, which is handy for deploying directly from configuration files checked into github:

kubectl create -f https://raw.githubusercontent.com/kubernetes/website/master/content/en/examples/application/nginx/nginx-deployment.yaml
deployment.apps/my-nginx created
Bulk operations in kubectl
Resource creation isn’t the only operation that kubectl can perform in bulk. It can also extract resource names from configuration files in order to perform other operations, in particular to delete the same resources you created:

kubectl delete -f https://k8s.io/examples/application/nginx-app.yaml
deployment.apps "my-nginx" deleted
service "my-nginx-svc" deleted
In the case of just two resources, it’s also easy to specify both on the command line using the resource/name syntax:

kubectl delete deployments/my-nginx services/my-nginx-svc
For larger numbers of resources, you’ll find it easier to specify the selector (label query) specified using -l or --selector, to filter resources by their labels:

kubectl delete deployment,services -l app=nginx
deployment.apps "my-nginx" deleted
service "my-nginx-svc" deleted
Because kubectl outputs resource names in the same syntax it accepts, it’s easy to chain operations using $() or xargs:

kubectl get $(kubectl create -f docs/concepts/cluster-administration/nginx/ -o name | grep service)
NAME           TYPE           CLUSTER-IP   EXTERNAL-IP   PORT(S)      AGE
my-nginx-svc   LoadBalancer   10.0.0.208   <pending>     80/TCP       0s
With the above commands, we first create resources under examples/application/nginx/ and print the resources created with -o name output format (print each resource as resource/name). Then we grep only the “service”, and then print it with kubectl get.

If you happen to organize your resources across several subdirectories within a particular directory, you can recursively perform the operations on the subdirectories also, by specifying --recursive or -R alongside the --filename,-f flag.

For instance, assume there is a directory project/k8s/development that holds all of the manifests needed for the development environment, organized by resource type:

project/k8s/development
├── configmap
│   └── my-configmap.yaml
├── deployment
│   └── my-deployment.yaml
└── pvc
    └── my-pvc.yaml
By default, performing a bulk operation on project/k8s/development will stop at the first level of the directory, not processing any subdirectories. If we had tried to create the resources in this directory using the following command, we would have encountered an error:

kubectl create -f project/k8s/development
error: you must provide one or more resources by argument or filename (.json|.yaml|.yml|stdin)
Instead, specify the --recursive or -R flag with the --filename,-f flag as such:

kubectl create -f project/k8s/development --recursive
configmap/my-config created
deployment.apps/my-deployment created
persistentvolumeclaim/my-pvc created
The --recursive flag works with any operation that accepts the --filename,-f flag such as: kubectl {create,get,delete,describe,rollout} etc.

The --recursive flag also works when multiple -f arguments are provided:

kubectl create -f project/k8s/namespaces -f project/k8s/development --recursive
namespace/development created
namespace/staging created
configmap/my-config created
deployment.apps/my-deployment created
persistentvolumeclaim/my-pvc created
If you’re interested in learning more about kubectl, go ahead and read kubectl Overview.

Using labels effectively
The examples we’ve used so far apply at most a single label to any resource. There are many scenarios where multiple labels should be used to distinguish sets from one another.

For instance, different applications would use different values for the app label, but a multi-tier application, such as the guestbook example, would additionally need to distinguish each tier. The frontend could carry the following labels:

     labels:
        app: guestbook
        tier: frontend
while the Redis master and slave would have different tier labels, and perhaps even an additional role label:

     labels:
        app: guestbook
        tier: backend
        role: master
and

     labels:
        app: guestbook
        tier: backend
        role: slave
The labels allow us to slice and dice our resources along any dimension specified by a label:

kubectl create -f examples/guestbook/all-in-one/guestbook-all-in-one.yaml
kubectl get pods -Lapp -Ltier -Lrole
NAME                           READY     STATUS    RESTARTS   AGE       APP         TIER       ROLE
guestbook-fe-4nlpb             1/1       Running   0          1m        guestbook   frontend   <none>
guestbook-fe-ght6d             1/1       Running   0          1m        guestbook   frontend   <none>
guestbook-fe-jpy62             1/1       Running   0          1m        guestbook   frontend   <none>
guestbook-redis-master-5pg3b   1/1       Running   0          1m        guestbook   backend    master
guestbook-redis-slave-2q2yf    1/1       Running   0          1m        guestbook   backend    slave
guestbook-redis-slave-qgazl    1/1       Running   0          1m        guestbook   backend    slave
my-nginx-divi2                 1/1       Running   0          29m       nginx       <none>     <none>
my-nginx-o0ef1                 1/1       Running   0          29m       nginx       <none>     <none>
kubectl get pods -lapp=guestbook,role=slave
NAME                          READY     STATUS    RESTARTS   AGE
guestbook-redis-slave-2q2yf   1/1       Running   0          3m
guestbook-redis-slave-qgazl   1/1       Running   0          3m
Canary deployments
Another scenario where multiple labels are needed is to distinguish deployments of different releases or configurations of the same component. It is common practice to deploy a canary of a new application release (specified via image tag in the pod template) side by side with the previous release so that the new release can receive live production traffic before fully rolling it out.

For instance, you can use a track label to differentiate different releases.

The primary, stable release would have a track label with value as stable:

     name: frontend
     replicas: 3
     ...
     labels:
        app: guestbook
        tier: frontend
        track: stable
     ...
     image: gb-frontend:v3
and then you can create a new release of the guestbook frontend that carries the track label with different value (i.e. canary), so that two sets of pods would not overlap:

     name: frontend-canary
     replicas: 1
     ...
     labels:
        app: guestbook
        tier: frontend
        track: canary
     ...
     image: gb-frontend:v4
The frontend service would span both sets of replicas by selecting the common subset of their labels (i.e. omitting the track label), so that the traffic will be redirected to both applications:

  selector:
     app: guestbook
     tier: frontend
You can tweak the number of replicas of the stable and canary releases to determine the ratio of each release that will receive live production traffic (in this case, 3:1). Once you’re confident, you can update the stable track to the new application release and remove the canary one.

For a more concrete example, check the tutorial of deploying Ghost.

Updating labels
Sometimes existing pods and other resources need to be relabeled before creating new resources. This can be done with kubectl label. For example, if you want to label all your nginx pods as frontend tier, simply run:

kubectl label pods -l app=nginx tier=fe
pod/my-nginx-2035384211-j5fhi labeled
pod/my-nginx-2035384211-u2c7e labeled
pod/my-nginx-2035384211-u3t6x labeled
This first filters all pods with the label “app=nginx”, and then labels them with the “tier=fe”. To see the pods you just labeled, run:

kubectl get pods -l app=nginx -L tier
NAME                        READY     STATUS    RESTARTS   AGE       TIER
my-nginx-2035384211-j5fhi   1/1       Running   0          23m       fe
my-nginx-2035384211-u2c7e   1/1       Running   0          23m       fe
my-nginx-2035384211-u3t6x   1/1       Running   0          23m       fe
This outputs all “app=nginx” pods, with an additional label column of pods’ tier (specified with -L or --label-columns).

For more information, please see labels and kubectl label.

Updating annotations
Sometimes you would want to attach annotations to resources. Annotations are arbitrary non-identifying metadata for retrieval by API clients such as tools, libraries, etc. This can be done with kubectl annotate. For example:

kubectl annotate pods my-nginx-v4-9gw19 description='my frontend running nginx'
kubectl get pods my-nginx-v4-9gw19 -o yaml
apiversion: v1
kind: pod
metadata:
  annotations:
    description: my frontend running nginx
...
For more information, please see annotations and kubectl annotate document.

Scaling your application
When load on your application grows or shrinks, it’s easy to scale with kubectl. For instance, to decrease the number of nginx replicas from 3 to 1, do:

kubectl scale deployment/my-nginx --replicas=1
deployment.extensions/my-nginx scaled
Now you only have one pod managed by the deployment.

kubectl get pods -l app=nginx
NAME                        READY     STATUS    RESTARTS   AGE
my-nginx-2035384211-j5fhi   1/1       Running   0          30m
To have the system automatically choose the number of nginx replicas as needed, ranging from 1 to 3, do:

kubectl autoscale deployment/my-nginx --min=1 --max=3
horizontalpodautoscaler.autoscaling/my-nginx autoscaled
Now your nginx replicas will be scaled up and down as needed, automatically.

For more information, please see kubectl scale, kubectl autoscale and horizontal pod autoscaler document.

In-place updates of resources
Sometimes it’s necessary to make narrow, non-disruptive updates to resources you’ve created.

kubectl apply
It is suggested to maintain a set of configuration files in source control (see configuration as code), so that they can be maintained and versioned along with the code for the resources they configure. Then, you can use kubectl apply to push your configuration changes to the cluster.

This command will compare the version of the configuration that you’re pushing with the previous version and apply the changes you’ve made, without overwriting any automated changes to properties you haven’t specified.

kubectl apply -f https://k8s.io/examples/application/nginx/nginx-deployment.yaml
deployment.apps/my-nginx configured
Note that kubectl apply attaches an annotation to the resource in order to determine the changes to the configuration since the previous invocation. When it’s invoked, kubectl apply does a three-way diff between the previous configuration, the provided input and the current configuration of the resource, in order to determine how to modify the resource.

Currently, resources are created without this annotation, so the first invocation of kubectl apply will fall back to a two-way diff between the provided input and the current configuration of the resource. During this first invocation, it cannot detect the deletion of properties set when the resource was created. For this reason, it will not remove them.

All subsequent calls to kubectl apply, and other commands that modify the configuration, such as kubectl replace and kubectl edit, will update the annotation, allowing subsequent calls to kubectl apply to detect and perform deletions using a three-way diff.

Note: To use apply, always create resource initially with either kubectl apply or kubectl create --save-config.
kubectl edit
Alternatively, you may also update resources with kubectl edit:

kubectl edit deployment/my-nginx
This is equivalent to first get the resource, edit it in text editor, and then apply the resource with the updated version:

kubectl get deployment my-nginx -o yaml > /tmp/nginx.yaml
vi /tmp/nginx.yaml
# do some edit, and then save the file

kubectl apply -f /tmp/nginx.yaml
deployment.apps/my-nginx configured

rm /tmp/nginx.yaml
This allows you to do more significant changes more easily. Note that you can specify the editor with your EDITOR or KUBE_EDITOR environment variables.

For more information, please see kubectl edit document.

kubectl patch
You can use kubectl patch to update API objects in place. This command supports JSON patch, JSON merge patch, and strategic merge patch. See Update API Objects in Place Using kubectl patch and kubectl patch.

Disruptive updates
In some cases, you may need to update resource fields that cannot be updated once initialized, or you may just want to make a recursive change immediately, such as to fix broken pods created by a Deployment. To change such fields, use replace --force, which deletes and re-creates the resource. In this case, you can simply modify your original configuration file:

kubectl replace -f https://k8s.io/examples/application/nginx/nginx-deployment.yaml --force
deployment.apps/my-nginx deleted
deployment.apps/my-nginx replaced
Updating your application without a service outage
At some point, you’ll eventually need to update your deployed application, typically by specifying a new image or image tag, as in the canary deployment scenario above. kubectl supports several update operations, each of which is applicable to different scenarios.

We’ll guide you through how to create and update applications with Deployments. If your deployed application is managed by Replication Controllers, you should read how to use kubectl rolling-update instead.

Let’s say you were running version 1.7.9 of nginx:

kubectl run my-nginx --image=nginx:1.7.9 --replicas=3
deployment.apps/my-nginx created
To update to version 1.9.1, simply change .spec.template.spec.containers[0].image from nginx:1.7.9 to nginx:1.9.1, with the kubectl commands we learned above.

kubectl edit deployment/my-nginx
That’s it! The Deployment will declaratively update the deployed nginx application progressively behind the scene. It ensures that only a certain number of old replicas may be down while they are being updated, and only a certain number of new replicas may be created above the desired number of pods. To learn more details about it, visit Deployment page.

