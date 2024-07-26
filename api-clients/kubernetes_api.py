"""
@Author: an.anurag@msn.com
@Date: 4-5-2023
"""

import time
from kubernetes import client

class KubernetesAPI:

    def __init__(self, host, port, api_key, ca_cert_path=False):
        """
        Initialization
        :param host:
        :param port:
        :param api_key:
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        self.ca_cert_path = ca_cert_path
        self.configuration = client.Configuration()

    def get_client(self):
        """
        Creates api client by configuring authentication with given cluster host
        :return:
        """
        self.configuration.api_key["authorization"] = self.api_key
        self.configuration.api_key_prefix['authorization'] = 'Bearer'
        self.configuration.host = f'https://{self.host}:{self.port}'
        self.configuration.verify_ssl = False
        # self.configuration.ssl_ca_cert = Path(self.ca_cert_path)
        return client.CoreV1Api(client.ApiClient(self.configuration))

    def get_pod_list(self, namespace):
        """
        Get all the pod in given namespace
        :param namespace:
        :return:
        """
        response = self.get_client().list_namespaced_pod(namespace=namespace)
        return response

    def get_config_map(self, name, namespace):
        response = self.get_client().read_namespaced_config_map(name=name, namespace=namespace)
        return response.data

    @staticmethod
    def create_configmap_object(dict_content):
        # Configureate ConfigMap metadata
        metadata = client.V1ObjectMeta(name="saas-framework-all", namespace="saas-framework")
        # Instantiate the configmap object
        configmap = client.V1ConfigMap(
            api_version="v1",
            kind="ConfigMap",
            data=dict_content,
            metadata=metadata
        )
        return configmap

    def create_or_update_config_map(self, **kwargs):
        """

        :param namespace:
        :param body:
        :return:
        """
        namespace = kwargs.get("namespace")
        config_map = k8s.create_configmap_object(**kwargs)
        response = self.get_client().list_namespaced_config_map(namespace=namespace)

        found = False
        for cm in response.to_dict()['items']:
            if cm['name'] == kwargs.get("name"):
                found = True

        if not found:
            self.get_client().create_namespaced_config_map(namespace=namespace, body=config_map)
        else:
            self.get_client().patch_namespaced_config_map(name=namespace, namespace=namespace, body=config_map)

    def list_namespaces(self):
        """
        List all namespaces
        :return:
        """
        response = self.get_client().list_namespace()
        return response
    
    def create_service_account(self, namespace, name):
        """
        Create service account
        :param namespace:
        :param name:
        :return:
        """
        body = client.V1ServiceAccount()
        body.metadata = client.V1ObjectMeta(name=name)
        response = self.get_client().create_namespaced_service_account(namespace=namespace, body=body)
        return response
    
    def create_secret(self, namespace, name, data):
        """
        Create secret 
        :param namespace:
        :param name:
        :param data:
        :return:
        """
        body = client.V1Secret()
        body.metadata = client.V1ObjectMeta(name=name)
        body.data = data
        response = self.get_client().create_namespaced_secret(namespace=namespace, body=body)
        return response

    def get_pod_status(self, namespace):

        total_pods = 0
        running_pods = 0
        pod_statuses = []

        while True:
            try:
                # Get list of pods in the namespace
                pods = self.get_client().list_namespaced_pod(namespace=namespace)

                # Reset counts
                total_pods = len(pods.items)
                running_pods = 0
                pod_statuses.clear()

                for pod in pods.items:
                    # Check if the pod is running
                    if pod.status.phase == "Running":
                        running_pods += 1
                    else:
                        pod_statuses.append({"name": pod.metadata.name, "status": pod.status.phase})

                if running_pods == total_pods:
                    return {"all_running": True, "pod_statuses": pod_statuses}

                # Wait for a few seconds before checking again
                time.sleep(1)

            except Exception as e:
                return {"error": f"Error occurred while fetching pod status: {e}"}


if __name__ == '__main__':
    # driver
    k8s = KubernetesAPI('api-server-ip', 'api-port', 'api-key')
    st = k8s.get_pod_status(namespace='dev')
    print(st)