import os
import json

from test_config import (
    ellip_notebooks_slug,
    ellip_studio_theia_slug,
    ellip_studio_lab_slug,
    ellip_studio_coder_slug,
    volume_sizes,
    rwx_storage_class,
)

from k8s import (
    delete_quota,
    set_quota,
    dispose_pvc,
    create_namespace,
    create_pvc,
    create_role,
    create_role_binding,
    get_configmap,
    create_secret,
    patch_service_account,
)


def get_default_url(profile_slug):

    default_url = "lab"

    if profile_slug in [ellip_studio_theia_slug]:

        return "theia"

    return default_url


def pre_spwan_hook(spawner):

    profile_slug = spawner.user_options.get("profile", None)

    namespace = f"jupyter-{spawner.user.name}"

    create_namespace(namespace)

    dispose_pvc(namespace=namespace)

    spawner.environment["JPY_DEFAULT_URL"] = get_default_url(profile_slug)

    # common context for studio and notebooks
    context_cms = {}

    context_cms["aws-config"] = {
        "mountPath": "/home/jovyan/.aws/config",
        "defaultMode": 0o0660,
        "readOnly": "true",
    }
    context_cms["aws-credentials"] = {
        "mountPath": "/home/jovyan/.aws/credentials",
        "defaultMode": 0o0660,
        "readOnly": "true",
    }
    context_cms["container-registry"] = {
        "mountPath": "/home/jovyan/.docker/config.json",
        "defaultMode": 0o0777,
        "readOnly": "false",
    }
    context_cms["workspace-rc"] = {
        "mountPath": "/home/jovyan/.workspacerc",
        "defaultMode": 0o0660,
        "readOnly": "false",
    }

    for key, cm_definition in context_cms.items():

        context_cm = get_configmap(namespace=namespace, name=key)

        if context_cm:

            if {
                "name": key,
                "mountPath": cm_definition["mountPath"],
                "subPath": key,
            } not in spawner.volume_mounts:
                spawner.log.info(f"Found {key} configMap, mounting")
                spawner.volume_mounts.extend(
                    [
                        {
                            "name": key,
                            "mountPath": cm_definition["mountPath"],
                            "subPath": key,
                        },
                    ]
                )
            if {
                "name": key,
                "configMap": {
                    "name": key,
                    "defaultMode": cm_definition["defaultMode"],
                },
            } not in spawner.volumes:
                spawner.volumes.extend(
                    [
                        {
                            "name": key,
                            "configMap": {
                                "name": key,
                                "defaultMode": cm_definition["defaultMode"],
                            },
                        },
                    ]
                )

            if key in ["workspace-rc"]:
                # set env vars
                for _key, value in json.loads(context_cm.data["workspace-rc"]).items():

                    spawner.environment[_key] = value

            if key in ["container-registry"] and profile_slug in [
                ellip_studio_theia_slug,
                ellip_studio_lab_slug,
            ]:
                secret_name = "container-rg-config"

                create_secret(
                    namespace=namespace,
                    secret_name=secret_name,
                    cred_payload=json.loads(context_cm.data["container-registry"]),
                )

                # TODO add secrets coming from container-registry configMap
                patch_service_account(namespace, secret_name)

    # the pod is now contextualized

    if profile_slug not in [
        ellip_studio_theia_slug,
        ellip_studio_lab_slug,
        ellip_studio_coder_slug,
    ]:
        # spwan pod for ellip notebooks
        return None

    # carry-on for calrissian setup
    # set the calrissian default volume size
    # volume_sizes = {}
    # volume_sizes[ellip_studio_theia_slug] = "25Gi"
    # volume_sizes[ellip_studio_lab_slug] = "25Gi"
    # volume_sizes[ellip_studio_coder_slug] = "25Gi"

    # check if there's a calrissian configMap
    calrissian_cm = get_configmap(namespace=namespace, name="calrissian-config")

    if calrissian_cm:

        for key, value in json.loads(calrissian_cm.data["calrissian-config"]).items():

            if key in ["CALRISSIAN_MAX_CPU", "CALRISSIAN_MAX_RAM"]:
                spawner.environment[key] = value

            if key in ["CALRISSIAN_VOLUME_SIZE"]:
                volume_sizes[ellip_studio_theia_slug] = value
                volume_sizes[ellip_studio_lab_slug] = value

    env = os.environ["JUPYTERHUB_ENV"].lower()
    spawner.environment["CALRISSIAN_POD_NAME"] = f"jupyter-{spawner.user.name}-{env}"

    roles = {}

    roles["pod-manager-role"] = {
        "verbs": ["create", "patch", "delete", "list", "watch"],
        "role_binding": "pod-manager-default-binding",
    }

    roles["log-reader-role"] = {
        "verbs": ["get", "list"],
        "role_binding": "log-reader-default-binding",
    }

    for role, value in roles.items():

        create_role(namespace=namespace, name=role, verbs=value["verbs"])
        create_role_binding(namespace=namespace, name=value["role_binding"], role=role)

    if profile_slug in volume_sizes.keys():
        # extend volumes if needed (it may happen that the claim is done
        # but the pod not triggered, e.g. timeout for lack of resources)
        for volume_suffix in ["tmp"]:

            volume_mount = {
                "name": f"calrissian-{volume_suffix}",
                "mountPath": f"/calrissian-{volume_suffix}",
            }
            if not volume_mount in spawner.volume_mounts:
                spawner.volume_mounts.extend(
                    [
                        {
                            "name": f"calrissian-{volume_suffix}",
                            "mountPath": f"/calrissian-{volume_suffix}",
                        }
                    ]
                )

            volume = {
                "name": f"calrissian-{volume_suffix}",
                "persistentVolumeClaim": {"claimName": f"calrissian-{volume_suffix}"},
            }
            if not volume in spawner.volumes:
                spawner.volumes.extend(
                    [
                        {
                            "name": f"calrissian-{volume_suffix}",
                            "persistentVolumeClaim": {
                                "claimName": f"calrissian-{volume_suffix}"
                            },
                        }
                    ]
                )

        create_pvc(
            namespace=namespace,
            size=volume_sizes[profile_slug],
            volumes=[f"calrissian-{volume_suffix}" for volume_suffix in ["tmp"]],
            rwx_storage_class=rwx_storage_class,
        )

    # Kubernetes quotas
    # quotas suspended until we learn how to use it
    # set_quota(namespace, profile_slug, resources)


def post_stop_hook(spawner):

    # note to future me
    # if there are pods running, the pvc will not be disposed
    # TODO list pods and kill them before invoking dispose_pvc()
    namespace = f"jupyter-{spawner.user.name}"

    quota_name = "user-quota"

    delete_quota(namespace, quota_name)

    dispose_pvc(namespace=namespace)
