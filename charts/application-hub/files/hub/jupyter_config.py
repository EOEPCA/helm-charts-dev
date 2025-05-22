import os
import sys

from tornado.httpclient import AsyncHTTPClient
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import yaml

from application_hub_context.app_hub_context import DefaultApplicationHubContext

configuration_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, configuration_directory)

from z2jh import (
    get_config,
    get_name,
    get_name_env,
)

config_path = "/usr/local/etc/applicationhub/config.yml"

def get_namespace_prefix():
    env = os.environ["JUPYTERHUB_ENV"].lower()  # Retrieve the JUPYTERHUB_ENV environment variable
    return f"{env}"  # Dynamically generate the namespace prefix

def get_jupyterhub_hub_host():
    fullname = os.environ.get("JUPYTERHUB_FULLNAME_OVERRIDE", "").strip().lower()
    namespace = get_namespace_prefix()
    if fullname:
        return f"{fullname}-hub.{namespace}"
    else:
        return f"hub.{namespace}"
    

def get_username_from_userinfo(userinfo):
    return (
        userinfo["email"]
        .split("@")[0]
        .replace(".", "")
        .replace("-", "")
        .replace("_", "")
    )

namespace_prefix = get_namespace_prefix()

def custom_options_form(spawner):
    spawner.log.info("Configure profile list")
    namespace = f"{namespace_prefix}-{spawner.user.name}"

    workspace = DefaultApplicationHubContext(
        namespace=namespace,
        spawner=spawner,
        config_path=config_path,
    )

    spawner.profile_list = workspace.get_profile_list()

    return spawner._options_form_default()

def namespace_exists(namespace_name):
    try:
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        v1.read_namespace(name=namespace_name)
        return True
    except ApiException as e:
        if e.status == 404:
            return False
        else:
            raise

def label_namespace(namespace, spawner):
    try:
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        body = {
            "metadata": {
                "labels": {
                    "eso": "enabled"
                }
            }
        }
        v1.patch_namespace(name=namespace, body=body)
        spawner.log.info(f"Namespace {namespace} patched with label eso=enabled")
    except ApiException as e:
        spawner.log.error(f"Failed to patch namespace {namespace}: {e}")


def pre_spawn_hook(spawner):
    profile_slug = spawner.user_options.get("profile", None)
    env = get_namespace_prefix()
    spawner.environment["CALRISSIAN_POD_NAME"] = f"hub-{env}-{spawner.user.name}"
    spawner.log.info(f"Using profile slug {profile_slug}")

    namespace = f"{env}-{spawner.user.name}"

    if namespace_exists(namespace):
        skip_check = True
        spawner.log.info(f"Namespace {namespace} already exists. Skipping creation.")
    else:
        skip_check = False
        spawner.log.info(f"Namespace {namespace} does not exist. It will be created.")

    workspace = DefaultApplicationHubContext(
        namespace=namespace,
        spawner=spawner,
        config_path=config_path,
        skip_namespace_check=skip_check
    )

    workspace.initialise()
    label_namespace(namespace, spawner)

    profile_id = workspace.config_parser.get_profile_by_slug(slug=profile_slug).id
    default_url = workspace.config_parser.get_profile_default_url(profile_id=profile_id)

    if default_url:
        spawner.log.info(f"Setting default url to {default_url}")
        spawner.default_url = default_url

def post_stop_hook(spawner):
    namespace = f"{namespace_prefix}-{spawner.user.name}"

    workspace = DefaultApplicationHubContext(
        namespace=namespace, spawner=spawner, config_path=config_path
    )
    spawner.log.info("Dispose in post stop hook")
    workspace.dispose()

c.JupyterHub.default_url = "spawn"

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

c.ConfigurableHTTPProxy.api_url = (
    f'http://{get_name("proxy-api")}:{get_name_env("proxy-api", "_SERVICE_PORT")}'
)

c.JupyterHub.tornado_settings = {
    "slow_spawn_timeout": 0,
}

jupyterhub_env = get_namespace_prefix().upper()
jupyterhub_hub_host = get_jupyterhub_hub_host()
jupyterhub_single_user_image = os.environ["JUPYTERHUB_SINGLE_USER_IMAGE_NOTEBOOKS"]

jupyterhub_auth_method = os.environ.get("JUPYTERHUB_AUTH_METHOD", "pam")
jupyterhub_oauth_callback_url = os.environ.get("JUPYTERHUB_OAUTH_CALLBACK_URL", "")
jupyterhub_oauth_client_id = os.environ.get("JUPYTERHUB_OAUTH_CLIENT_ID", "")
jupyterhub_oauth_client_secret = os.environ.get("JUPYTERHUB_OAUTH_CLIENT_SECRET", "")

# Authentication
c.LocalAuthenticator.create_system_users = True
c.Authenticator.admin_users = {"jovyan"}
# Deprecated
c.Authenticator.allowed_users = {"jovyan"}
c.Authenticator.allow_existing_users = True

if jupyterhub_auth_method == "sso":
    c.JupyterHub.authenticator_class = "oauthenticator.generic.GenericOAuthenticator"
    c.GenericOAuthenticator.oauth_callback_url = jupyterhub_oauth_callback_url
    c.GenericOAuthenticator.client_id = jupyterhub_oauth_client_id
    c.GenericOAuthenticator.client_secret = jupyterhub_oauth_client_secret
    c.GenericOAuthenticator.auto_login = True
    c.GenericOAuthenticator.username_claim = get_username_from_userinfo
elif jupyterhub_auth_method == "pam":
    c.JupyterHub.authenticator_class = "jupyterhub.auth.PAMAuthenticator"
    c.PAMAuthenticator.service = "login"
    c.PAMAuthenticator.open_sessions = True
    c.PAMAuthenticator.encoding = "utf8"
elif jupyterhub_auth_method == "dummy":
    c.JupyterHub.authenticator_class = "dummy"
else:
    raise ValueError(
        "No suitable authentication method defined. Please check the value of the environment variable JUPYTERHUB_AUTH_METHOD"
    )

c.ConfigurableHTTPProxy.auth_token = get_config("proxy.secretToken")
c.JupyterHub.cookie_secret_file = "/srv/jupyterhub/cookie_secret"
c.JupyterHub.cleanup_servers = False
c.JupyterHub.allow_named_servers = True
c.JupyterHub.ip = "0.0.0.0"
c.JupyterHub.hub_ip = "0.0.0.0"
c.JupyterHub.hub_connect_ip = jupyterhub_hub_host
c.JupyterHub.cleanup_servers = False

c.JupyterHub.services = [
    {
        "name": "idle-culler",
        "admin": True,
        "command": [sys.executable, "-m", "jupyterhub_idle_culler", "--timeout=3600"],
    }
]

c.JupyterHub.log_level = "DEBUG"

c.JupyterHub.spawner_class = "kubespawner.KubeSpawner"
c.KubeSpawner.environment = {
    "JUPYTER_ENABLE_LAB": "true",
}

c.KubeSpawner.uid = 1001
c.KubeSpawner.fs_gid = 100
c.KubeSpawner.hub_connect_ip = jupyterhub_hub_host

c.KubeSpawner.privileged = True
c.KubeSpawner.allow_privilege_escalation = True

c.KubeSpawner.service_account = "default"
c.KubeSpawner.start_timeout = 60 * 15
c.KubeSpawner.image = jupyterhub_single_user_image
c.KubernetesSpawner.verify_ssl = True
c.KubeSpawner.pod_name_template = (
    "hub-" + get_namespace_prefix() + "-{username}" + "-{servername}"
)

c.KubeSpawner.user_namespace_template = get_namespace_prefix() + "-{username}"

c.KubeSpawner.enable_user_namespaces = True
c.KubeSpawner.user_namespace_labels = {"eso": "enabled"}

c.KubeSpawner.image_pull_secrets = ["cr-config"]

c.KubeSpawner.options_form = custom_options_form
c.KubeSpawner.pre_spawn_hook = pre_spawn_hook
c.KubeSpawner.post_stop_hook = post_stop_hook

c.JupyterHub.template_paths = [
    "/opt/jupyterhub/template",
    "/usr/local/share/jupyterhub/templates",
]
