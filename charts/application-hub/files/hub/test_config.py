ellip_studio_theia_slug = "ellip-studio-theia"
ellip_studio_lab_slug = "ellip-studio-lab"
ellip_notebooks_slug = "ellip-notebooks"
ellip_studio_coder_slug = "ellip-coder"

#rwx_storage_class = "openebs-kernel-nfs-scw"
rwx_storage_class = "openebs-nfs-test"
# defines the resources per profile
resources = {}

resources[ellip_notebooks_slug] = {
    "requests.cpu": "1",
    "requests.memory": "16G",
    "limits.cpu": "16",
    "limits.memory": "16G",
    "requests.storage": "16Gi",
    "services.nodeports": "0",
}

resources[ellip_studio_theia_slug] = {
    "requests.cpu": "4",
    "requests.memory": "16G",
    "limits.cpu": "16",
    "limits.memory": "16G",
    "requests.storage": "150Gi",
    "services.nodeports": "0",
}

resources[ellip_studio_lab_slug] = {
    "requests.cpu": "4",
    "requests.memory": "16G",
    "limits.cpu": "16",
    "limits.memory": "16G",
    "requests.storage": "150Gi",
    "services.nodeports": "0",
}

resources[ellip_studio_coder_slug] = {
    "requests.cpu": "4",
    "requests.memory": "16G",
    "limits.cpu": "16",
    "limits.memory": "16G",
    "requests.storage": "150Gi",
    "services.nodeports": "0",
}


volume_sizes = {}
volume_sizes[ellip_studio_theia_slug] = "25Gi"
volume_sizes[ellip_studio_lab_slug] = "25Gi"
volume_sizes[ellip_studio_coder_slug] = "75Gi"
