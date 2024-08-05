import requests

from config_manager import ConfigManager


class ArtifactoryAPI:

    config = ConfigManager()

    def __init__(self, **kwargs):
        self.host = self.config['artifactory']['api']['endpoint']
        self.access_token = kwargs.get('access_token', None)
        if not self.access_token:
            self.access_token = self.config['artifactory']['api']['access-token']
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def get_image_tag_list(self, repo_name, image_name):
        """

        :param repo_name:
        :param image_name:
        :param tag_to_check:
        :return:
        """
        url = self.host + f"/docker/{repo_name}/v2/{image_name}/tags/list"
        response = requests.get(url, headers=self.headers)
        try:
            if response.status_code == 404:
                errors = response.json()
                if errors:
                    raise ValueError(f"{errors['message']} {repo_name}")

            elif response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            raise

    def set_item_property(self, repo, image, tag, **kwargs):
        """
        Set properties for the given image
        """
        product = kwargs.get('product')
        bundle_version = kwargs.get('version')
        url = self.host + f"/storage/{repo}/{image}/{tag}?properties=product={product};bundle-version={bundle_version}"
        response = requests.put(url)
        if response.status_code == 204:
            print(f"info: properties updated for {image}")

    def promote_docker_image(self, source_repo, target_repo, image_name, source_tag, target_tag, copy):
        """
        Promotes the docker image from source repo to target repo
        """

        url = self.host + f"/docker/{source_repo}/v2/promote"
        payload = {
            "targetRepo": target_repo,
            "dockerRepository": image_name,
            "tag": source_tag,
            "targetTag": target_tag,
            "copy": copy
        }

        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 200:
            return True, "Success"
        return False, response.json()['errors'][0]['message']

    def copy_artifact(self, source_repo, target_repo, object_name):
        url = self.host + f"/copy/{source_repo}/{object_name}?to={target_repo}"
        print(url)
      
        response = requests.post(url, headers=self.headers)
        print(response.json())
        if response.status_code == 200:
            return True
        return False

    def aql_query(self, data):
        """
        Executes the AQL query
        :param data: The AQL query to be executed
        :return: json response of the query
        """

        url = self.host + f"/search/aql"
        response = requests.post(url, headers=self.headers, data=data)
        return response.json()

    def delete_artifact(self, artifact_url):
        """
        Deletes the artifact from the artifactory
        :param artifact_url: The url of the artifact to be deleted in Artifactory
        :return: status code of the delete request
        """

        response = requests.delete(artifact_url, headers=self.headers)
        return response.status_code
        # if response.status_code == 204:
        #     print("info: artifact deleted")
        #     return response.status_code
        # print("error: artifact deletion unsuccessful")


if __name__ == '__main__':
    arti = ArtifactoryAPI()
    response = arti.copy_artifact("some-local-repo", "some-local-repo-2", "image-name")
    print(response)

