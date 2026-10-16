in all stateless services pods have service names + hash(to make it new)
stateful will make pods like : servicename-001, servicename-002, servicename-003, etc. 

For backend, frontend etc. components => stateless
For postgres, mongodb => statefull

"ClusterIP = None" => headless 
iIn headless, we use kind as a Stateful Set, no random names for pods, replicas. 


pod/web-stateful-0       
pod/web-stateful-1    
pod/web-stateful-2 
Now if I delete pod/web-stateful-0, then new pod of same name will be created. 
This is stateful/headless service. Mention ClusterIP: None in service. Never in deployment


Now, ClusterIp: None, so therefore we cant access it from either inside or outside cluster 

minikube service service/web-service-headless
❌  Exiting due to SVC_NOT_FOUND: Service 'service/web-service-headless' was not found in 'default' namespace.
You may select another namespace by using 'minikube service service/web-service-headless -n <namespace>'. Or list out all the services using 'minikube service list'