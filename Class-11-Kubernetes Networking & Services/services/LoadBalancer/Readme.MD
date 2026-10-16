In Local Development (Minikube / Docker Desktop):
On local Minikube, there is no real cloud provider. EXTERNAL-IP will stay in <pending> state unless you run the Minikube tunnel daemon.

For NodePort, same for ClusterIP:
kubectl get svc/web-service-nodeport 
NAME                   TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
web-service-nodeport   NodePort   10.106.243.40   <none>        80:30080/TCP   11s

For LoadBalancer:
kubectl get svc/web-service-loadbalancer 
NAME                       TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
web-service-loadbalancer   LoadBalancer   10.102.34.173   <pending>     80:32754/TCP   7s

Now to make it from pending to get an IP, start minikube tunnel. 
Then do minikube service web-service-loadbalancer


minikube service web-service-loadbalancer --url => http://127.0.0.1:54554


