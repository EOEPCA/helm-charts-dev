# Application Hub Helm Chart

This repository provides a Helm chart and supporting configurations for deploying JupyterHub on Kubernetes, tailored for the ApplicationHub platform. It includes features for secure user authentication, resource management, and dynamic user profiles.

---

## Features

### Based on JupyterHub

This chart relies on the official JupyterHub Helm chart (`v4.0.0`) as its umbrella chart. It includes all core JupyterHub features and extends them with custom scheduling configurations.

---

## Installation

### Prerequisites

- A running Kubernetes cluster (`v1.23.0` or later).
- Helm CLI (`v3.0` or later).
- Sufficient cluster resources for the scheduler and placeholder pods.

### Steps

1. **Add the Chart Repository**  

   If the chart is hosted in a Helm repository, add it:

   ```
   helm repo add application-hub <YOUR HELM CHART REPOSITORY>
   helm repo update
   ```

2. **Fetch Dependencies**

   The chart relies on the JupyterHub Helm chart. Ensure dependencies are fetched:

    ```
    helm dependency update
    ```

3. **Generate the necessary Enviroment Variable**

   Make sure to define the following environment variables to ensure correct behavior of your JupyterHub deployment:

   1. JUPYTERHUB_CRYPT_KEY
      
      Used to encrypt user cookies and tokens.
      Generate it with the following command:
      ```
      openssl rand -hex 32
      ```
      and copy the result string in the values.yaml file: https://github.com/EOEPCA/helm-charts-dev/blob/develop/charts/application-hub/values.yaml#L59


   2. JUPYTERHUB_ENV
      
      Represents the Kubernetes namespace where JupyterHub is deployed.

   3. JUPYTERHUB_FULLNAME_OVERRIDE
      
      * Must match the fullnameOverride field defined in your values.yaml.
      * Used to determine the internal name of the JupyterHub services, such as the hub API.
      * Ensures correct DNS resolution within the Kubernetes cluster.

4. **Service Account and Cluster Permissions**

   This Helm chart automatically creates a Kubernetes service account for the JupyterHub hub component. That service account is then linked to cluster-wide permissions so that JupyterHub can manage resources as needed.

   Specifically:
      * The service account is created with a name you specify (e.g. application-hub).
      * A ClusterRoleBinding is also created, which assigns that service account the cluster-admin role.

   This setup allows the JupyterHub hub to:
      * Create and manage user namespaces
      * Access and create Kubernetes Secrets (e.g., tokens, credentials)

   Example configuration in values.yaml:
   ```
   hub:
      serviceAccount:
         create: true
         name: application-hub
   ```
   This ensures that JupyterHub has the access it needs to manage dynamic, per-user environments across the cluster.

4. **Install the Chart**

   Run the following command to deploy the application:
   
   ```
   helm install application-hub ./chart-directory --values values.yaml
   ```
   This command installs the Helm chart in the current namespace. Use the *--namespace* flag if a specific namespace is required.

5. **Verify Deployment** 

   Monitor the deployment using *kubectl*:
   ```
   kubectl get pods -n <namespace>
   kubectl get svc -n <namespace>
   ```
   Ensure that all pods are running, and the services are properly exposed.

6. **Access JupyterHub**

   Access the deployed JupyterHub using the URL defined in the Ingress configuration. For example:
   ```
   https://<your-ingress-hostname>
   ```

   or use port forward of the proxy-public service:
   ```
   kubectl port-forward svc/<proxy-public-service> 8080:80 -n <namespace>
   ```
