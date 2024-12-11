# Application Hub Helm Chart

This repository provides a Helm chart and supporting configurations for deploying JupyterHub on Kubernetes, tailored for the ApplicationHub platform. It includes features for secure user authentication, resource management, and dynamic user profiles.

---

## Features

### Based on JupyterHub

This chart relies on the official JupyterHub Helm chart (`v3.3.7`) as its umbrella chart. It includes all core JupyterHub features and extends them with custom scheduling configurations.

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

3. **Install the Chart**

   Run the following command to deploy the application:
   
   ```
   helm install application-hub ./chart-directory --values values.yaml
   ```
   This command installs the Helm chart in the current namespace. Use the *--namespace* flag if a specific namespace is required.

4. **Verify Deployment** 

   Monitor the deployment using *kubectl*:
   ```
   kubectl get pods -n <namespace>
   kubectl get svc -n <namespace>
   ```
   Ensure that all pods are running, and the services are properly exposed.

5. **Access JupyterHub**

   Access the deployed JupyterHub using the URL defined in the Ingress configuration. For example:
   ```
   https://<your-ingress-hostname>

   ```