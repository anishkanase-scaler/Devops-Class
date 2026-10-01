![alt text](image.png)
![alt text](image-1.png)
![alt text](image-2.png)
![alt text](image-3.png)

kubectl rollout status deploy/app-rolling
kubectl rollout history deploy/app-rolling
kubectl get pods -l app=app-rolling --show-labels => to get a label/version 
of an app -l = label
kubectl rollout undo deploy/app-rolling => takes me back to previous version
kubectl rollout undo deploy/app-rolling --to-revision=x 
kubectl rollout history deploy/app-rolling --revision=13





1. Difference between StatefulSet, Deployment, DaemonSet
2. Difference between ReplicaSet, Deployment
3. Deployment Strategies
4. DaemonSet (needs 2 servers)
5. TroubleShooting
6. Service Types (5 types)
7. Research on FQDN and Core DNS.




1. Difference between StatefulSet, Deployment, DaemonSet:
Deployment:
A Deployment manages identical, stateless Pods.
Pod Naming: Pods receive random hash names (e.g., app-rolling-577b6bf6db-6rbs4).
Pod Replacement: If a Pod crashes or is deleted, the Deployment creates a completely new Pod with a new random name and a new internal IP address.


StatefulSet:
A StatefulSet manages Pods that require a permanent network identity and persistent storage.
Pod Naming: Pods receive strict, sequential, numbered names (e.g., db-0, db-1, db-2).
Pod Replacement: If db-1 crashes, the StatefulSet spins up a replacement Pod named exactly db-1. The network identity never changes.



DaemonSet
A DaemonSet ignores replica counts and binds Pods directly to the Nodes themselves.
Pod Count: You do not set a replicas field. The number of Pods is strictly dictated by the number of Nodes in your cluster.






2. Difference between ReplicaSet, Deployment
Replica Set is jus for scaling pods up and down, no migrations can be done, and also no history is preserved so we cant go to our previous version if we want to. 
We almost never create ReplicaSet directly, we create a Deployment which will further create the ReplicaSet for us.

A Deployment sits on top of ReplicaSets to provide automated updates and rollbacks. 
It orchestrates updates across multiple ReplicaSets. 

Rolling Updates: When you change a Deployment from v1 to v2, it creates a brand new ReplicaSet for v2. It then slowly scales up the new v2 ReplicaSet while simultaneously scaling down the old v1 ReplicaSet, ensuring zero downtime.
Rollback History: Deployments keep your old ReplicaSets around but scale them to 0 Pods. When you ran kubectl rollout undo, the Deployment simply scaled the v2 ReplicaSet down to 0, and scaled the old v1 ReplicaSet back up to 3.




Q3. Deployment Strategies:

1. Rollout: In this the manager creates one v2 pod, and once its healthy, it deletes the v1 pod.
It repeats this process until all pods are v2. No downtime, but some users will see v1 
for a time and after refreshing they may see v2 because both are running simultaneously.
No double server space needed. 
We know that a service will distribute the load evenly among all pods, if we have 4 pods, and in that 1 is new (v2) and others are v1, then 25% random traffic hits v2.
Rollout is random, and canary is sticky, any random user can get any random ui. 
Rolling Updates are "dumb" and fast

2. Canary: This is different from rollout bcs it gives the v2 to some specific 5% or x% users, and they will see only v2 version and others will see only v1 version as of now, even after refresh, unline in rollout. Bcs here v2 is given to specific fixed users and canary remembers who have been given what. 
Canary is sticky, if 5% users are getting v2, canary remembers those 5% users. 
Canaries are "smart" and slow

3. Blue-green: So here we keep the old version untouched, but also make a new version and then we spin up a complete, identical v2 environment (Green) next to it. Once this is fully tested, we shift all 100% users here, no downtime, but double server space, expensive. 

4. Recreate: Here, u first scale down all pods of v1, then we have a downtime, and then once all v1 are dead, it boosts up the new version. 
No extra space, but downtime is there. We use this when the first and second version uses completely different database structures and running both at the same time would corrupt your data, you must shut down v1 completely before starting v2.

5. Shadow (The "Ghost" Strategy)
Users only interact with v1, but in the background, router takes copy of their request and the v2 receives copy of their request by router. Users never see v2, but developers get to see how v2 handles real-world production traffic and load.






Q4. Service Types (5 types)
