import os

from test_config import (
    ellip_notebooks_slug,
    ellip_studio_theia_slug,
    ellip_studio_lab_slug,
    ellip_studio_coder_slug,
)

# custom profile list
def custom_options_form(spawner):
    # returns the profile list based on the groups the user belongs to
    # based on;
    # - https://discourse.jupyter.org/t/tailoring-spawn-options-and-server-configuration-to-certain-users/8449
    # - https://discourse.jupyter.org/t/accessing-user-groups-from-pre-spawn-hook/9723

    spawner.log.info("Configure profile list")

    spawner.profile_list = []

    spawner.profile_list.extend(
        [
            {
                "display_name": "Studio Coder version 0.8",
                "slug": ellip_studio_coder_slug,
                "default": True,
                "kubespawner_override": {
                    "cpu_limit": 4,
                    "mem_limit": "8G",
                    "image": "cr.terradue.com/ellip-studio/studio-coder:0.8",
                },
            }
        ]
    )

    spawner.profile_list.extend(
        [
            {
                "display_name": "jh-theia",
                "slug": "jh-theia",
                "default": False,
                "kubespawner_override": {
                    "cpu_limit": 2,
                    "mem_limit": "4G",
                    "image": "docker.io/fabricebrito/jh-theia-python:0.7",
                },
            }
        ]
    )

    spawner.profile_list.extend(
        [
            {
                "display_name": "jh-streamlit",
                "slug": "streamlit",
                "default": False,
                "kubespawner_override": {
                    "cpu_limit": 2,
                    "mem_limit": "4G",
                    "image": "docker.io/fabricebrito/jh-streamlit",
                },
            }
        ]
    )

    user_groups = [group.name for group in spawner.user.groups]

    if "ellip-notebooks" in user_groups:
        spawner.profile_list.extend(
            [
                {
                    "display_name": "Ellip Notebooks",
                    "slug": ellip_notebooks_slug,
                    "default": False,
                    "kubespawner_override": {
                        "cpu_limit": 2,
                        "mem_limit": "4G",
                        "image": os.environ["JUPYTERHUB_SINGLE_USER_IMAGE_NOTEBOOKS"],
                    },
                }
            ]
        )

    if "ellip-studio" in user_groups:
        spawner.profile_list.extend(
            [
                {
                    "display_name": "Ellip Studio Theia",
                    "slug": ellip_studio_theia_slug,
                    "kubespawner_override": {
                        "cpu_limit": 4,
                        "mem_limit": "8G",
                        "image": os.environ["JUPYTERHUB_SINGLE_USER_IMAGE_STUDIO"],
                    },
                },
                {
                    "display_name": "Ellip Studio Lab",
                    "slug": ellip_studio_lab_slug,
                    "kubespawner_override": {
                        "cpu_limit": 4,
                        "mem_limit": "8G",
                        "image": os.environ["JUPYTERHUB_SINGLE_USER_IMAGE_STUDIO"],
                    },
                },
            ]
        )

    return spawner._options_form_default()
