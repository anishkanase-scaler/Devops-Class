![alt text](image.png)
empty-dir is a temporary storage, once lifecyle of pod ends(created, running, delete)entire storage we have with empty-dir gets deleted.
If we create smthg inside data dir, it will get deleted once pod gets deleted. 

![alt text](image-1.png)

Also, we cant directly apply once we change the volume path (mountPath), we will have to delete that pod and then apply it. 


PV(storage/capacity): this is like a hard disk, which will be the storage we have, inside a cluster. eg: Persistent vol = 20GB
PVC: Node will claim storage from PV. eg: Pod will claim 500mb of storage from PV. This is the space used by a POD only, and inside that used by any container, service(db, frontend, backend, etc.) => This is PVC. 

![alt text](image-2.png)
NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM                 STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
persistentvolume/pvc-655f8fa2-086f-4d35-b0d7-20fbfc953c8d   500Mi      RWO            Delete           Bound       default/student-pvc   standard       <unset>                          11d
persistentvolume/student-pv                                 1Gi        RWO            Retain           Available                                        <unset>                          11d

NAME                                STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
persistentvolumeclaim/student-pvc   Bound    pvc-655f8fa2-086f-4d35-b0d7-20fbfc953c8d   500Mi      RWO            standard       <unset>                 11d




A service will have to do all these:
1. search which types of pvc it will have to use
2. search which types of pv it will have to use
There will be many pv,pcs. Searching is lengthy. 

So, we use "claimPloicy", add jus one term:   "storageClassName: standard"
This will create the pv automatically, no need to manually create pv file. 

HPA: Horizontal Pod AutoScaler
Jus mention the min and max replicas we want to scale, set boundaries, use HPA, this will automatically scale the replicas as per the no of users. 



kubectl run load-generator \
  --image=busybox:1.36 \
  --restart=Never \
  -- /bin/sh -c \
  "while true; do wget -q -O- http://hpa-demo-service; done"
This is the load generator

![alt text](image-3.png)
![alt text](image-4.png)


kubectl top pods:
NAME                        CPU(cores)   MEMORY(bytes)   
hpa-demo-5d6676989b-2xnvl   40m          8Mi             
hpa-demo-5d6676989b-7nfcv   40m          8Mi             
load-generator              796m         7Mi             

