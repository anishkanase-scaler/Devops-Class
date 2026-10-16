Headless => used in stateful
NodePort => used while testing(develpoment/staging)
LoadBalancer => used in real production
ExternalName => used when I have my own domain, own product, not a client
ClusterIP => used for local purposes 


FQDN: If I have same service names in all environment: dev, staging, prod, how do I differentiate ?
Type servicename.environment.objecttype.cluster.local => Minikube
Type servicename.environment.objecttype.cluster.aws.eks => AWS


