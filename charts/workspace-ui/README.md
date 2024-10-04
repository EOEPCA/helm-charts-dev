# Helm chart for the Workspace UI incl. Storage Layer

## Prerequisites

The following secret must be present in the namespace:

```
apiVersion: v1
kind: Secret
metadata:
  name: <namespace name or provided via values.s3CredentialsSecretName>
  namespace: <namespace>
data:
  AWS_ACCESS_KEY_ID: <corresponding base64encoded value>
  AWS_SECRET_ACCESS_KEY: <corresponding base64encoded value>
  AWS_ENDPOINT_URL: <corresponding base64encoded value>
  AWS_REGION: <corresponding base64encoded value>
```

The Kubernetes CRD `sources.package.r` must be installed on the cluster.