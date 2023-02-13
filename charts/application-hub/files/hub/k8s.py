from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.config.config_exception import ConfigException
from time import sleep
import base64
import json


def delete_quota(namespace, quota_name):

    try:
        config.load_incluster_config()  # raises if not in cluster
    except ConfigException:
        config.load_kube_config()  # for local debug/test purposes

    api_client = client.ApiClient()

    try:
        response = client.CoreV1Api().delete_namespaced_resource_quota(
            namespace=namespace, name=quota_name
        )
    except ApiException as e:
        if e.status == 404:
            pass
        else:
            raise e


def set_quota(namespace, profile_slug, resources):

    quota_name = "user-quota"

    delete_quota(namespace, quota_name)

    try:
        config.load_incluster_config()  # raises if not in cluster
    except ConfigException:
        config.load_kube_config()  # for local debug/test purposes

    api_client = client.ApiClient()

    resource_quota = client.V1ResourceQuota(
        spec=client.V1ResourceQuotaSpec(hard=resources[profile_slug])
    )
    resource_quota.metadata = client.V1ObjectMeta(namespace=namespace, name=quota_name)

    try:
        response = client.CoreV1Api().create_namespaced_resource_quota(
            namespace, resource_quota
        )
        return response
    except ApiException as e:
        if e.status == 409:
            pass
        else:
            raise e


def dispose_pvc(namespace: str):

    try:
        config.load_incluster_config()  # raises if not in cluster
    except ConfigException:
        config.load_kube_config()  # for local debug/test purposes

    #api_client = client.ApiClient()

    pvcs = client.CoreV1Api().list_namespaced_persistent_volume_claim(
        namespace=namespace, watch=False
    )

    for pvc in pvcs.items:

        if pvc.metadata.name in [
            "calrissian-tmp",
            "calrissian-input",
            "calrissian-output",
        ]:

            try:
                response = client.CoreV1Api().delete_namespaced_persistent_volume_claim(
                    name=pvc.metadata.name,
                    namespace=namespace,
                    body=client.V1DeleteOptions(),
                )
            except ApiException as e:
                if e.status == 404:
                    pass
                else:
                    raise e


def create_role(
    namespace: str,
    name: str,
    verbs: list,
    resources: list = ["pods", "pods/log"],
    api_groups: list = ["*"],
):

    try:
        config.load_incluster_config()  # raises if not in cluster
    except ConfigException:
        config.load_kube_config()  # for local debug/test purposes)

    api_client = client.ApiClient()

    metadata = client.V1ObjectMeta(name=name, namespace=namespace)

    rule = client.V1PolicyRule(
        api_groups=api_groups,
        resources=resources,
        verbs=verbs,
    )

    body = client.V1Role(metadata=metadata, rules=[rule])

    try:
        response = client.RbacAuthorizationV1Api(api_client).create_namespaced_role(
            namespace, body, pretty=True
        )
        return response

    except ApiException as e:
        if e.status == 409:
            pass
        else:
            raise e


def create_role_binding(namespace, name: str, role: str):

    try:
        config.load_incluster_config()  # raises if not in cluster
    except ConfigException:
        config.load_kube_config()  # for local debug/test purposes

    api_client = client.ApiClient()

    metadata = client.V1ObjectMeta(name=name, namespace=namespace)

    role_ref = client.V1RoleRef(api_group="", kind="Role", name=role)

    subject = client.models.V1Subject(
        api_group="",
        kind="ServiceAccount",
        name="default",
        namespace=namespace,
    )

    body = client.V1RoleBinding(
        metadata=metadata, role_ref=role_ref, subjects=[subject]
    )

    try:
        response = client.RbacAuthorizationV1Api(
            api_client
        ).create_namespaced_role_binding(namespace, body, pretty=True)
        return response
    except ApiException as e:
        if e.status == 409:
            pass
        else:
            raise e


def create_pvc(namespace, size, volumes, rwx_storage_class):

    if size is None:
        size = "7Gi"

    try:
        config.load_incluster_config()  # raises if not in cluster
    except ConfigException:
        config.load_kube_config()  # for local debug/test purposes

    api_client = client.ApiClient()

    pvcs = [
        {
            "name": volume,
            "size": size,
            "storage_class": rwx_storage_class,
            "access_modes": ["ReadWriteMany"],
        }
        for volume in volumes
    ]
    # pvcs = [{
    #         "name": "calrissian-tmp",
    #         "size": size,
    #         "storage_class": "longhorn",
    #         "access_modes": ["ReadWriteMany"],
    #     }]
    # pvcs = [
    #     {
    #         "name": "calrissian-tmp",
    #         "size": size,
    #         "storage_class": "longhorn",
    #         "access_modes": ["ReadWriteMany"],
    #     },
    #     {
    #         "name": "calrissian-input",
    #         "size": size,
    #         "storage_class": "longhorn",
    #         "access_modes": ["ReadWriteMany"],
    #     },
    #     {
    #         "name": "calrissian-output",
    #         "size": size,
    #         "storage_class": "longhorn",
    #         "access_modes": ["ReadWriteMany"],
    #     },
    # ]

    for pvc in pvcs:

        metadata = client.V1ObjectMeta(name=pvc["name"], namespace=namespace)

        spec = client.V1PersistentVolumeClaimSpec(
            access_modes=pvc["access_modes"],
            resources=client.V1ResourceRequirements(requests={"storage": pvc["size"]}),
        )

        spec.storage_class_name = pvc["storage_class"]

        body = client.V1PersistentVolumeClaim(metadata=metadata, spec=spec)

        try:
            response = client.CoreV1Api(
                api_client
            ).create_namespaced_persistent_volume_claim(namespace, body, pretty=True)

        except ApiException as e:
            if e.status == 409:
                pass
            else:
                raise e

        created = False

        while not created:
            try:
                response = client.CoreV1Api(
                    api_client
                ).read_namespaced_persistent_volume_claim(
                    name=pvc["name"], namespace=namespace
                )
                created = True
            except ApiException as e:
                if e.status == 404:
                    sleep(3)


def create_namespace(namespace: str):

    try:
        config.load_incluster_config()  # raises if not in cluster
    except ConfigException:
        config.load_kube_config()  # for local debug/test purposes

    api_client = client.ApiClient()

    try:
        body = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace))
        response = client.CoreV1Api(api_client).create_namespace(
            body=body, async_req=False
        )
        return response
    except ApiException as e:
        if e.status == 409:
            pass
        else:
            raise e


def get_configmap(
    namespace: str,
    name: str,
):

    try:
        config.load_incluster_config()  # raises if not in cluster
    except ConfigException:
        config.load_kube_config()  # for local debug/test purposes

    api_client = client.ApiClient()

    try:
        return client.CoreV1Api(api_client).read_namespaced_config_map(
            namespace=namespace, name=name
        )
    except ApiException as e:
        if e.status == 404:
            return None
        raise e


def create_secret(namespace: str, secret_name: str, cred_payload):

    try:
        config.load_incluster_config()  # raises if not in cluster
    except ConfigException:
        config.load_kube_config()  # for local debug/test purposes

    api_client = client.ApiClient()

    delete_secret(namespace=namespace, secret_name=secret_name)

    data = {
        ".dockerconfigjson": base64.b64encode(
            json.dumps(cred_payload).encode()
        ).decode()
    }

    try:
        metadata = {"name": secret_name, "namespace": namespace}

        secret = client.V1Secret(
            api_version="v1",
            data=data,
            kind="Secret",
            metadata=metadata,
            type="kubernetes.io/dockerconfigjson",
        )

        client.CoreV1Api(api_client).create_namespaced_secret(
            namespace=namespace, body=secret
        )

    except ApiException as e:
        if e.status == 409:
            pass
        else:
            raise e


def delete_secret(namespace, secret_name):

    try:
        config.load_incluster_config()  # raises if not in cluster
    except ConfigException:
        config.load_kube_config()  # for local debug/test purposes

    api_client = client.ApiClient()

    try:
        response = client.CoreV1Api(api_client).delete_namespaced_secret(
            namespace=namespace, name=secret_name
        )
    except ApiException as e:
        if e.status == 404:
            pass
        else:
            raise e


def patch_service_account(namespace, secret_name):
    # adds a secret to the namespace default service account
    try:
        config.load_incluster_config()  # raises if not in cluster
    except ConfigException:
        config.load_kube_config()  # for local debug/test purposes

    api_client = client.ApiClient()

    service_account_body = client.CoreV1Api(api_client).read_namespaced_service_account(
        name="default", namespace=namespace
    )

    if service_account_body.secrets is None:
        service_account_body.secrets = []

    if service_account_body.image_pull_secrets is None:
        service_account_body.image_pull_secrets = []

    service_account_body.secrets.append({"name": secret_name})
    service_account_body.image_pull_secrets.append({"name": secret_name})

    try:
        client.CoreV1Api(api_client).patch_namespaced_service_account(
            name="default", namespace=namespace, body=service_account_body, pretty=True
        )
    except ApiException as e:
        raise e
