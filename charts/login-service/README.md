# HELM Chart for the Login Service

## Prerequisites

* This chart requires Docker Engine 1.8+ in any of their supported platforms.  Please see vendor requirements [here for more information](https://docs.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker).
* At least 2GB of RAM. Make sure to assign enough memory to the Docker VM if you're running on Docker for Mac or Windows.

## Chart Components
* It's a nested Helm Chart with more than one service and deployments
* Creates a full Login Service Instance (Gluu based)
* Exposes the oxtrust service for access to the UI

## Installing the Chart

You can install the chart with the release name `id4eo` in `default` namespace. The entire installation of the Login Service will take around 20 minutes to be up depending on the resources of the machine.

```console
$ helm install id4eo charts/login-service
```
> Note - If you do not specify a name, helm will select a name for you.

The installation will apply all charts described within the login-service chart.
  * Config-Init: This instance will stand as a Job that will ingest the first configuration data for the other services to feed from in installation. 
  * OpenDJ: The WrenDS image will create the backend for the LDAP database and will comunicate with the presistence Job to apply all custom changes done in Gluu.
  * Persistence: This Job will run aside the OpenDJ pod to ingest the custom data into the database.
  * OxPassport: This Pod will allow the passport feature to the hole Login Service, it applies to the login feature.
  * OxAuth: This deployment will set up the Authentication and Authorization service. Needs the previous pods to be running.
  * OxTrust: This is the last to be installed and will offer the main Gluu UI from where the application can be accessed.

### Installed Components

You can use `kubectl get` to view all of the installed components.

```console
$ kubectl get all | grep id4eo
pod/id4eo-config-27zwh                  0/1     Completed   0          164m
pod/id4eo-opendj-init-ss-0              1/1     Running     0          164m
pod/id4eo-oxauth-6946d5c4b8-vv2ms       1/1     Running     1          164m
pod/id4eo-oxpassport-6b44dddd4b-79t2d   1/1     Running     0          164m
pod/id4eo-oxtrust-ss-0                  1/1     Running     1          164m
pod/id4eo-persistence-init-ss-k7qmw     0/1     Completed   0          164m

deployment.apps/id4eo-oxauth       1/1     1            1           164m

deployment.apps/id4eo-oxpassport   1/1     1            1           164m
replicaset.apps/id4eo-oxauth-6946d5c4b8       1         1         1       164m
replicaset.apps/id4eo-oxpassport-6b44dddd4b   1         1         1       164m


statefulset.apps/id4eo-opendj-init-ss   1/1     164m
statefulset.apps/id4eo-oxtrust-ss       1/1     164m
job.batch/id4eo-config                1/1           3m35s      164m
job.batch/id4eo-persistence-init-ss   1/1           11m        164m
```

## Connecting to the Login Service

1. Follow the documentation of the Login-Service Repository in GitHub: [Wiki Login Service](https://github.com/EOEPCA/um-login-service/wiki).

## Values

The values can be edited in each sub-chart or on most generic at the parent level.
The configuration parameters in this section control the base domain and most general configuration for every sub-chart.

| Parameter                               | Description                                                                                    | Default                          |
| --------------------------------------- | ---------------------------------------------------------------------------------------------- | -------------------------------- |
| global.namespace                    | Name where the pdp instance is going to install in the cluster  | `default`                              |
| global.serviceName                    | Name for the main OpenDJ service  | `opendj`                              |
| global.nginxIp | IP for the nginx ingress controller                                                        | `10.0.2.15`  
| global.oxAuthServiceName                    | Name for the main OxAuth service  | `oxauth`                              |
| global.persistenceServiceName                    | Name for the main persistence Job service  | `persistence`                              |
| global.oxTrustServiceName                    | Name for the main OxTrust service  | `oxtrust`                              |
| global.domain                            | Name for the sso_url UMA Compliant | `myplatform.eoepca.org`                        |
| global.gluuLdapUrl                    | URL where the LDAP backend is running  | `opendj:1636`                              |
| global.gluuMaxRamFraction             | Number of fractions of RAM, where 1 is the 100% of the requested RAM | `1` |
| global.configAdapterName            | Name for the k8s config adapter | `kubernetes`        |
| global.configSecretAdapter            | Name for the k8s secret adapter | `kubernetes`        |
| global.provisioner  | Clustering provisioner name | `k8s.io/minikube-hostpath`  |


## Config

For the Config Job the main configuration will focus on certificate signatures and base LDAP customization.

  ```yaml
  enabled: true
  domain: myplatform.eoepca.org
  ldapType: opendj
  countryCode: ES
  state: Madrid
  city: Tres Cantos
  adminPass: <pwd>
  ldapPass: <pwd>
  email: eoepca@deimos-space.com
  orgName: Deimos Space S.L.U.
  gluuConfAdapter: kubernetes
  redisPass: <pwd>
  ```

## OpenDJ

  ```yaml
  enabled: true
  gluuCacheType: NATIVE_PERSISTENCE
  gluuRedisEnabled: false
  volumeClaim:
    name: um-login-service-pvc
  persistence:
    enabled: true
    image:
      repository: eoepca/um-login-persistence
      pullPolicy: IfNotPresent
      tag: "v0.9.0"
  ```

  ## OxAuth

  ```yaml
  oxauth:
  enabled: true
  dynamicStorage: true
  volumeClaim:
    name: um-login-service-pvc
  ```

  ## OxTrust

  ```yaml
  oxtrust:
  enabled: true
  dynamicStorage: true
  volumeClaim:
    name: um-login-service-pvc
  ```

  ## Nginx

  The Nginx controller can be used as Ingress for load balancing, currently will use the tls-certificates and specify the domain name for the Login Service.

  ```yaml
  nginx:
    enabled: true
    ingress:
      enabled: true
      annotations: {}
      path: /
      hosts:
        - myplatform.eoepca.org
      tls: 
      - secretName: tls-certificate
        hosts:
          - myplatform.eoepca.org
    resources: {}
    autoscaling:
      enabled: false
      minReplicas: 1
      maxReplicas: 100
      targetCPUUtilizationPercentage: 80
      # targetMemoryUtilizationPercentage: 80
    nodeSelector: {}
    tolerations: []
    affinity: {}
    tags:
      redis: false
  ```

## Liveness and Readiness

The Login Service instance has liveness and readiness checks specified in each sub-chart, it may need to be specified in some specifics services that takes some time to be ready such as OxAuth, OxTrust and OpenDJ.


