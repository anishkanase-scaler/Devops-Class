1. minikube ip
2. kubectl exec -it pod/curl-client -- sh and inside that curl http://web-service-clusterip:8080 
OR
kubectl exec -it curl-client -- curl -s http://web-service-clusterip:8080
You will get the Nginx home page. 
You created the pod-client-pod, and entered the container inside it, then u can access the service using the service name and the service ip

web-service-clusterip   ClusterIP   10.101.146.72   <none>        8080/TCP   21m
this becomes http://web-service-clusterip:8080

So now from another container(client-pod), Im able to access the service ip. 
But from browser, Im not able to do it:
anishkanase@Anishkas-MacBook-Air ClusterIP % curl http:/web-service-clusterip:8080
curl: (6) Could not resolve host: web-service-clusterip

This is bcs, curl command is able to access only via the containers, inside that cluster, 
the client-pod container and service are inside one cluster, so Im able to ping service via tha container only. 

So, do port-forwarding: 
kubectl port-forward service/web-service-clusterip 8080:8080
first port: local
second port: port of the service, you want to access. 



