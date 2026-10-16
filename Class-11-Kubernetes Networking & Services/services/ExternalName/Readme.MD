NAME                                TYPE           CLUSTER-IP       EXTERNAL-IP      PORT(S)        AGE
service/external-database-service   ExternalName   <none>           api.github.com   <none>         92s
service/web-service-clusterip       ClusterIP      10.105.0.125     <none>           8080/TCP       15s
service/web-service-loadbalancer    LoadBalancer   10.111.196.186   127.0.0.1        80:32666/TCP   29s
service/web-service-nodeport        NodePort       10.107.69.90     <none>           80:30080/TCP   7s 
service/web-service-headless        ClusterIP      <none>           <none>           80/TCP         4s
All have Cluster IP, except the External Name. External Name and Load Balancer have an External IP as well. 


minikube service is mainly meant to access Kubernetes Services that expose a pod/application, such as NodePort or LoadBalancer. An ExternalName Service doesn't have a selector, endpoints, or a port exposed by Minikube—it is essentially a DNS alias.


This is because ClusterIP: None, 
Now, ClusterIp: None, so therefore we cant access it from either inside or outside cluster 
minikube service external-database-service: this command didnt work.

❌  Exiting due to SVC_NOT_FOUND: Service '{default external-database-service [] []}' was not found in 'default' namespace.
You may select another namespace by using 'minikube service {default external-database-service [] []} -n <namespace>'. Or list out all the services using 'minikube service list'




Entering into the client pod and checking the external ip url  

1. Use "curl https://external-database-service -k" => -k tells u to skip TLS certificate verification.
(
    <div id="s">
        <a href="https://support.github.com">Contact Support</a> &mdash;
        <a href="https://githubstatus.com">GitHub Status</a> &mdash;
        <a href="https://twitter.com/githubstatus">@githubstatus</a>
      </div>
)


2. kubectl exec -it dns-test-client -- sh
~ $ nslookup external-database-service
Server:         10.96.0.10
Address:        10.96.0.10:53

** server can't find external-database-service.svc.cluster.local: NXDOMAIN
** server can't find external-database-service.cluster.local: NXDOMAIN
** server can't find external-database-service.cluster.local: NXDOMAIN
** server can't find external-database-service.svc.cluster.local: NXDOMAIN

external-database-service.default.svc.cluster.local     canonical name = api.github.com
external-database-service.default.svc.cluster.local     canonical name = api.github.com
Name:   api.github.com
Address: 20.207.73.85
