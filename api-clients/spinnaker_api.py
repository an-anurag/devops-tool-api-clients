"""
@Author: an.anurag@msn.com
@Date: 4-5-2023
"""

import requests

from config_manager import ConfigManager

requests.packages.urllib3.disable_warnings()


class SpinnakerAPI:

    config = ConfigManager()

    def __init__(self, crt_path, key_path) -> None:
        self.host = self.config["spinnaker"]["host"]
        self.crt = crt_path
        self.key = key_path

    def get_pipeline_config(self, application_name, pipeline_name):
        """
        Get pipeline config JSON
        :param application_name:
        :param pipeline_name:
        :return:
        """

        url = f"{self.host}/applications/{application_name}/pipelineConfigs/{pipeline_name}"
        try:
            response = requests.get(url=url, verify=False, cert=(self.crt, self.key))
            if response.status_code == 200:
                return response.json()
        except TimeoutError as err:
            return err

    def create_pipeline(self, payload):
        """
        Creates Spinnaker pipeline with given json config as a payload
        :param payload:
        :return:
        """
        # update bundle pipeline
        url = f"{self.host}/pipelines?staleCheck=true"
        response = requests.post(url=url, json=payload, verify=False, cert=(self.crt, self.key))
        if response.status_code == 200:
            return True
        return False

    def run_pipeline(self, application, pipeline, parameters=None):
        """
        Triggers pipeline
        :param application:
        :param pipeline:
        :return:
        """
        url = f"{self.host}/pipelines/{application}/{pipeline}"
        payload = {
            "parameters": parameters
        }
        response = requests.post(url, verify=False, json=payload, cert=(self.crt, self.key))
        if "ref" in response.json():
            return True
        return False


