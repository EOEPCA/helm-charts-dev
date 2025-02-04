# Helm Chart for KNative-Operator

This chart is responsible for deploying KNative-Operator in order to support the functionality offered by the Notification and Automation Building Block

## Prerequisites

The prerequisites for this chart are:
- Kubernetes v1.28 or newer
- The Kubernetes cluster must have access to the internet. This is needed for fetching container images. Future releases will support using private container registrys in order to support airgaped deployments.

## Installing the Chart

You can install the chart with the release name `knative-operator` in `knative-operator` namespace as below.

```console
$ helm install knative-operator charts/knative-operator --namespace knative-operator
```

## Resources

You can specify the resource limits for this chart in the values.yaml file.  Make sure you comment out or remove the curly brackets from the values.yaml file before specifying resource limits.
Example:

```yaml
knativeOperator:
  knativeOperator:
    resources:
    limits:
        cpu: 2
        memory: 4Gi
    requests:
        cpu: 1
        memory: 2Gi
```
