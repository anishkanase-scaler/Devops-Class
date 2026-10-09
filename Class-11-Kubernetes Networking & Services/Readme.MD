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





1. Difference between ReplicaSet, Deployment
2. Difference between StatefulSet, Deployment, DaemonSet
3. ReplicaSet vs Service
4. FQDN
5. CoreDNS
6. Deployment Strategies



Q-1. Difference between ReplicaSet, Deployment
Replica Set is jus for scaling pods up and down, no migrations can be done, and also no history is preserved so we cant go to our previous version if we want to. 
We almost never create ReplicaSet directly, we create a Deployment which will further create the ReplicaSet for us.

A Deployment sits on top of ReplicaSets to provide automated updates and rollbacks. 
It orchestrates updates across multiple ReplicaSets. 

Rolling Updates: When you change a Deployment from v1 to v2, it creates a brand new ReplicaSet for v2. It then slowly scales up the new v2 ReplicaSet while simultaneously scaling down the old v1 ReplicaSet, ensuring zero downtime.
Rollback History: Deployments keep your old ReplicaSets around but scale them to 0 Pods. When you ran kubectl rollout undo, the Deployment simply scaled the v2 ReplicaSet down to 0, and scaled the old v1 ReplicaSet back up to 3.

A ReplicaSet's main job is keeping the required number of Pods running. 
If replicaset.yml has pods = 3, so the ReplicaSet says: “I need 3 Pods matching this label.” If one Pod dies, the ReplicaSet creates another one to bring the count back to 3.

A Deployment is a higher-level controller that manages ReplicaSets, but the Deployment doesn't directly do all the Pod management itself. It creates and manages a ReplicaSet, and that ReplicaSet manages the actual Pods.
Now for rolling updates , deployment will create new replicas, with new images, number of pods etc. 


Purpose: A ReplicaSet’s purpose is to maintain a specified number of identical Pods and make sure the desired number of Pods are always running. A Deployment’s purpose is to manage application releases and updates. It provides a higher-level way to manage the application and its versions.
Pod management: A ReplicaSet directly manages Pods. For example, if replicas: 3, it ensures 3 matching Pods exist. A Deployment manages Pods indirectly by managing the ReplicaSet that creates and maintains them. So the relationship is Deployment → ReplicaSet → Pods.
Scaling: Both support scaling. With a ReplicaSet, changing the replicas value changes the number of Pods that ReplicaSet maintains. With a Deployment, scaling the Deployment changes the desired number of Pods through its managed ReplicaSet.
Rolling updates: Rolling updates are a feature of Deployments, not the main responsibility of a ReplicaSet. When the application version changes, the Deployment creates a new ReplicaSet for the new version and gradually scales down the old ReplicaSet while scaling up the new one.
Relationship: A Deployment manages ReplicaSets, and each ReplicaSet manages the Pods for a particular version of the application. Therefore, the hierarchy is Deployment → ReplicaSets → Pods.







Q-2. Difference between StatefulSet, Deployment, DaemonSet:
Deployment:
A Deployment manages identical, stateless Pods.
Pod Naming: Pods receive random hash names (e.g., app-rolling-577b6bf6db-6rbs4).
Pod Replacement: If a Pod crashes or is deleted, the Deployment creates a completely new Pod with a new random name and a new internal IP address.


StatefulSet:
A StatefulSet manages Pods that require a permanent network identity and persistent storage.
Pod Naming: Pods receive strict, sequential, numbered names (e.g., db-0, db-1, db-2).
Pod Replacement: If db-1 crashes, the StatefulSet spins up a replacement Pod named exactly db-1. The network identity never changes.


DaemonSet
Pod Count: A DaemonSet scales automatically when nodes are added or removed, because it tries to maintain one Pod per eligible node


Use cases: A Deployment is used for stateless applications where Pods are interchangeable, such as web servers and APIs. A DaemonSet is used when you want a Pod to run on every node or on selected nodes, commonly for logging, monitoring, or node-level agents. A StatefulSet is used for stateful applications where each Pod needs a stable identity and often persistent storage, such as databases and distributed systems.

Pod creation: A Deployment creates and manages a specified number of interchangeable Pods through ReplicaSets. A DaemonSet creates a Pod on each eligible node automatically, so the number of Pods depends mainly on the number of nodes rather than a replicas value. A StatefulSet creates Pods with stable, predictable identities such as db-0, db-1, and db-2, and manages them in an ordered way.

Scaling: A Deployment scales by changing the number of replicas, such as 3 → 5 Pods. A DaemonSet scales automatically when nodes are added or removed, because it tries to maintain one Pod per eligible node. A StatefulSet scales by changing the number of replicas, but the Pods have ordered and stable identities, so scaling from 2 to 3 creates the next Pod with its own identity, such as db-2.

Networking: Deployment Pods are usually accessed through a Service and are interchangeable; their individual identities and IPs are not normally important. DaemonSet Pods can also be accessed through Services, but they are often used for node-local tasks and may communicate with applications on the same node. StatefulSet Pods have stable network identities, usually provided through a Headless Service, so a specific Pod can be reached consistently, such as db-0.

Storage: Deployments are generally used with stateless applications, so Pods usually do not need their own persistent storage. DaemonSets may use node-level storage such as host-mounted directories for things like collecting logs. StatefulSets are specifically suited for persistent storage because each Pod can have its own PersistentVolumeClaim, allowing its data to remain associated with that Pod even when the Pod is recreated.

Examples: A Deployment example is an Nginx web server or backend API with multiple identical Pods. A DaemonSet example is a log collector such as Fluent Bit or a node-monitoring agent running on every node. A StatefulSet example is PostgreSQL, MySQL, MongoDB, Kafka, or another application where each instance needs stable identity and persistent data.







Q-3. ReplicaSet vs Service
ReplicaSet responsibility: A ReplicaSet is responsible for maintaining a desired number of identical Pods. For example, if replicas: 3, it ensures that 3 matching Pods are running. If a Pod crashes or is deleted, the ReplicaSet creates a replacement Pod.

Service responsibility: A Service provides a stable network endpoint for a group of Pods. It uses labels and selectors to identify which Pods should receive traffic and distributes requests among those Pods.

Why a Service is required: Pods are temporary and their IP addresses can change whenever they are recreated. Without a Service, clients would have to keep track of changing Pod IPs. Pods behind it can be created, deleted, or replaced.

How traffic reaches Pods: A client sends a request to the Service. The Service uses its selector to find matching Pods and routes the request to one of their Pod IPs. For example, Service → selector app=nginx → matching Pods → Pod IP. In a typical Kubernetes setup, kube-proxy implements this Service routing/load-balancing on the nodes.






Q-4: FQDN
FQDN stands for Fully Qualified Domain Name. It is the complete domain name of a resource, including all the parts required to uniquely identify it in the DNS hierarchy. In Kubernetes, FQDNs are commonly used to identify Services and Pods within the cluster.

Kubernetes automatically creates DNS records for Services. A Service can be accessed using a DNS name such as `service-name.namespace-name.svc.cluster.local`. For example, `backend.default.svc.cluster.local` refers to a Service named `backend` in the `default` namespace. A normal Service name resolves to its ClusterIP.

Kubernetes DNS is namespace-based, which means the namespace is part of the DNS name. If a Pod and Service are in the same namespace, the Pod can usually communicate with the Service using only its short name, such as `backend`. Kubernetes uses the Pod's DNS search domains to expand this into something like `backend.default.svc.cluster.local`. To access a Service in another namespace, you can use `backend.production` or the complete FQDN `backend.production.svc.cluster.local`.

Pod-to-Service communication is preferred over direct Pod-to-Pod communication because Pod IP addresses are not permanent. Pods can be deleted and recreated with different IPs, while the Service provides a stable DNS name and network endpoint. For example, a frontend Pod can communicate with `backend.default.svc.cluster.local`, and the Service then forwards the request to one of the matching backend Pods.

The Kubernetes Service FQDN follows the general format `service.namespace.svc.cluster.local`. For example, `my-service.default.svc.cluster.local`, `backend.production.svc.cluster.local`, and `database.staging.svc.cluster.local` are valid examples. `service` is the Service name, `namespace` identifies where the Service exists, `svc` indicates that it is a Service, and `cluster.local` is the cluster's DNS domain.





Q-5: Core DNS
CoreDNS is the DNS server used in Kubernetes for providing DNS-based service discovery inside the cluster. It is written in Go and uses a plugin-based architecture. Kubernetes uses the CoreDNS Kubernetes plugin to create and resolve DNS records for Kubernetes resources.

Kubernetes uses CoreDNS because Pods and Services can change over time. Pod IP addresses can change when Pods are recreated, so applications should not depend on individual Pod IPs. Instead, they can communicate using a stable Service DNS name such as `backend.default.svc.cluster.local`. CoreDNS resolves that name to the appropriate Kubernetes Service information.

For example, if a frontend Pod wants to communicate with a Service named `backend` in the `default` namespace, it can query `backend`. Kubernetes DNS search domains can expand this to `backend.default.svc.cluster.local`. CoreDNS then resolves the name so the frontend can reach the backend Service.


In simple terms: **CoreDNS is the internal DNS system of Kubernetes. Pods ask CoreDNS for names such as `backend.default.svc.cluster.local`, and CoreDNS resolves those names so Pods can discover and communicate with Services without needing to know changing Pod IP addresses.**




Q-6. Deployment Strategies:

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






