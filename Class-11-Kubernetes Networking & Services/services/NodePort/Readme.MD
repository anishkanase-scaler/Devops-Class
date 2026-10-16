1. kubectl get all -l app=web-clusterip
2. kubectl get endpoints <service-name>
3. kubectl exec -it <pod-name> -- sh
4. minikube service web-service-nodeport --url http://127.0.0.1:52315 , 52315=> this is Docker
web-service-nodeport   NodePort    10.109.22.109   <none>        80:30080/TCP   5m23s   app=web-nodeport
If we do 10.109.22.109:52315, we get the needed output. 

** minikube servce web-service-nodeport ** => will always open the needed page. 





What happens in Node Port is:
1. The request will go to the node with the port:30080(or whatever mentioned) from my laptop. 
2. "Anything coming into 30010 actually belongs to the web-service-clusterip on internal port 8080"
So, the service will receive the request.
3. Then this service looks at its Endpoints, and will find all pods with labels: web-nodeport, means if all pods are in different nodes, then it means this request will be sent to all the nodes. 
4. Then it will change destination of request packet to the Pod's internal IP Addr, which is port 80, and then Nginx receives the request, processes the webpage, and sends the response back down the chain to your laptop.

