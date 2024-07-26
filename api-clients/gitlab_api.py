import gitlab
from gitlab import exceptions
from gitlab.v4.objects.projects import Project
from config_manager import ConfigManager


class GitlabAPI:

    def __init__(self, **kwargs) -> None:
        self.gitlab_configs = ConfigManager()['gitlab']
        self.user_token = kwargs.get('token')

    @staticmethod
    def _form_project_name(arg1, arg2):
        """Helper"""
        return str(arg1 + "/" + arg2)

    def login(self):
        """
        Get the Gitlab client
        :return: None
        """
        token = self.gitlab_configs['auth-token']
        if self.user_token:
            return gitlab.Gitlab(url=self.gitlab_configs["host"], private_token=self.user_token)
        return gitlab.Gitlab(url=self.gitlab_configs["host"], private_token=token)

    def get_users_emails(self, user_token):
        """
        Gives the all user emails in list
        :return:
        """
        user_emails = []
        user_list = self.login().users.list(get_all=True)
        for item in user_list:
            user_emails.append(item.email)
        return user_emails

    def get_project_with_id(self, project_id):
        """
        Get the gitlab project by id
        :param project_id:
        :return:
        """

        try:
            project = self.login().projects.get(project_id)
            return project
        except gitlab.exceptions.GitlabGetError:
            raise

    def get_project_with_name(self, namespace, project_name):
        """
        Fetch the gitlab project
        :param project_name
        :param namespace
        :return:
        """
        try:
            project = self.login().projects.get(self._form_project_name(namespace, project_name))
            return project
        except gitlab.exceptions.GitlabGetError:
            raise

    def get_project(self, namespace, project_name, project_id=None):
        """
        Fetch the gitlab project
        :param project_id:
        :param project_name
        :param namespace
        :return:
        """
        try:
            return self.get_project_with_name(namespace, project_name)
        except gitlab.exceptions.GitlabAuthenticationError:
            raise ValueError("error: unauthorized")
        except gitlab.exceptions.GitlabGetError:
            if project_id:
                try:
                    return self.get_project_with_id(project_id)
                except gitlab.exceptions.GitlabGetError:
                    raise
            raise

    def is_project_exist(self, namespace, project_name, folder=None):
        """

        :param namespace:
        :param project_name:
        :return:
        """
        project = self.get_project(namespace, project_name)
        if not isinstance(project, Project):
            return False
        return True

    def get_commits(self, namespace, project_name, branch):
        """
        Fetch the latest commit sha (short id)
        :param branch:
        :param project_name:
        :param namespace
        :return:
        """
        project = self.get_project(namespace, project_name)
        commits = project.commits.list(ref_name=branch, get_all=False)
        return commits


    def get_commit_details(self, namespace, project_name, commit_id):
        """
        Fetch the commit details
        :param commit_id:
        :param project_name:
        :param namespace
        :return:
        """
        project = self.get_project(namespace, project_name)
        commit = project.commits.get(commit_id)
        return commit


    def get_commit_diff(self, namespace, project_name, commit_id):
        """
        Fetch the commit diff
        :param commit_id:
        :param project_name:
        :param namespace
        :return:
        """
        project = self.get_project(namespace, project_name)
        commit = project.commits.get(commit_id)
        return commit.diff(get_all=True)

    def tag_project(self, namespace, project_name, tag, branch):
        """
        tag = project.tags.create({'tag_name': '1.0', 'ref': 'main'})
        gitlab.v4.objects.tags.ProjectTag
        :return:
        """
        try:
            result = self.get_project(namespace, project_name).tags.create({"tag_name": tag, "ref": branch})
            return result
        except exceptions.GitlabCreateError as err:
            return err

    def get_project_tags(self, namespace, project_name):
        """
        Get all tags of given project
        """
        project = self.get_project(namespace, project_name)
        return project.tags.list()

    def create_commit_to_repo(self, namespace, project_name, data):
        """
        Create Gitlab commit, with given data
        :param project_name:
        :param namespace
        :param data: {
            'branch': 'branch',
            'commit_message': 'commit_message',
            'actions': [
                {
                    'action': 'create',
                    'file_path': 'file_path',
                    'content': content,
                }
            ]
        }
        :return:
        """
        try:
            project = self.get_project(namespace, project_name)
            project.commits.create(data)
            return True
        except exceptions.GitlabCreateError as err:
            return err

    def create_file_in_repo(self, namespace, project_name, **kwargs):
        """
        Create file in given repo
        :return:
        data = {
            "filepath": f"{product}/{service_group}/{manifest_name}",
            "branch": branch,
            "content": bundle_yaml,
            "email": self.author_email,
            "author": self.author,
            "commit_message": f"Added {manifest_name}"
        }
        created = self.gitlab.create_file_in_repo(group, project_name=project_name, **data)

        """
        try:
            project = self.get_project(namespace, project_name)
            project.files.create({
                'file_path': kwargs.get('filepath'),
                'branch': kwargs.get("branch"),
                'content': kwargs.get("content"),
                'author_email': kwargs.get("email"),
                'author_name': kwargs.get("author"),
                'commit_message': kwargs.get("commit_message")
            })
            return True
        except gitlab.exceptions.GitlabCreateError as err:
            return err

    def get_file_from_repo(self, namespace, project_name, branch, filepath):
        """
        Fetch the content of the file git repo
        :param project_name
        :param namespace
        :param branch
        :param filepath
        :return: file content
        """
        try:
            project = self.get_project(namespace, project_name)
            f = project.files.get(file_path=filepath, ref=branch)
            return f.decode().decode()
        except gitlab.exceptions.GitlabGetError as err:
            return err

    def get_repository_filetree(self, namespace, project_name, branch):
        """
        Get file tree from given repo
        :param project_name:
        :param branch
        :param namespace
        :return:
        """
        project = self.get_project(namespace, project_name)
        return project.repository_tree(ref=branch, recursive=True)

    def get_dir_filetree(self, namespace, project_name, branch, path, get_all=False):
        """
        Get file tree from given repo
        :param project_name:
        :param branch
        :param namespace
        :return:
        """
        project = self.get_project(namespace, project_name)
        return project.repository_tree(ref=branch, path=path, recursive=True, get_all=get_all)

    def commit_changes_to_file(self, namespace, project_name, branch, file_path, contents, commit_message, project_id=None):
        """
        Commit changes to file given by branch and file_path
        :param project_id:
        :param namespace:
        :param project_name:
        :param branch:
        :param file_path:
        :param contents:
        :param commit_message:
        :return:
        """
        project = self.get_project(namespace, project_name, project_id=project_id)
        rel_file = project.files.get(file_path=file_path, ref=branch)
        rel_file.content = contents
        rel_file.save(branch=branch, commit_message=commit_message)

    def create_branch(self, namespace, project_name, branch, parent_branch):
        """

        :param namespace:
        :param project_name:
        :param branch:
        :param parent_branch:
        :return:
        """
        try:
            project = self.get_project(namespace, project_name)
            branch = project.branches.create({'branch': branch, 'ref': parent_branch})
            return branch
        except gitlab.exceptions.GitlabCreateError as err:
            return err

    def create_mr(self, namespace, project_name, source_branch, target_branch, title):
        """
        Creates the MR on given project
        :param namespace:
        :param project_name:
        :param source_branch:
        :param target_branch:
        :param title:
        :return:
        """
        try:
            project = self.get_project(namespace, project_name)
            mr = project.mergerequests.create(
                {
                    'source_branch': source_branch,
                    'target_branch': target_branch,
                    'title': title,

                }
            )
            return mr

        except gitlab.exceptions.GitlabCreateError as err:
            return err

    def get_merge_requests(self, namespace, project, state=None, order_by=None, sort=None):
        """
        Gets all the MRs of the given project
        :param namespace:
        :param project:
        :param state: state of the MR. It can be one of all, merged, opened, closed or locked
        :param order_by: sort by created_at or updated_at
        :param sort: asc, desc
        :return:None
        """
        project = self.get_project(namespace, project)
        mrs = project.mergerequests.list(state=state, order_by=order_by, sort=sort, get_all=True)
        return mrs

    def get_branches(self, namespace, project):
        """
        Get all branches for given project
        :param namespace:
        :param project:
        :return:
        """
        project = self.get_project(namespace, project)
        branches = project.branches.list(get_all=True)
        return branches

    @staticmethod
    def delete_mr(mr_obj):
        """
        Deletes the MR identified by given iid
        :param mr_obj: Gitlab MR Obj
        :return:None
        """

        mr_obj.delete()
        print(f"MR deleted - {mr_obj.iid}")

    @staticmethod
    def delete_branch(branch_obj):
        """
        Delete the branch identified by branch object
        :param branch_obj:
        :return:
        """
        branch_obj.delete()
        print(f"branch deleted - {branch_obj.name}")

    def get_project_pipelines(self, namespace, project_name, branch):
        """
        Gets all the pipeline for given branch
        :param group:
        :param project_name:
        :param project_id:
        :param branch:
        :return:
        """
        project = self.get_project(namespace, project_name)
        pipelines = project.pipelines.list(iterator=True, ref=branch)
        return pipelines

    def has_project_variable(self, namespace, project_name, key):
        """
        Check if a CI/CD variable already exists in a GitLab project.
        :param group
        :param project_name: GitLab project object
        :param key: Variable key
        :return: True if the variable already exists, False otherwise
        """
        project = self.get_project(namespace, project_name)
        existing_variables = project.variables.list()
        for variable in existing_variables:
            if variable.key == key:
                return True
        return False

    def add_project_variables(self, namespace, project_name, variables):
        """
        Add multiple CI/CD variables to a GitLab project.

        :param namespace: GitLab namespace (e.g., group or user)
        :param project_name: GitLab project name
        :param variables: List of variable definitions, each containing key, value, environment_scope, and protected
        :return: True if all variables are added successfully or already exist, False otherwise
        """
        try:
            project = self.get_project(namespace, project_name)
            for variable_data in variables:

                key = variable_data['key']

                if not self.has_project_variable(project, key):
                    variable_data['environment_scope'] = variable_data.get('environment_scope', None)
                    variable_data['protected'] = variable_data.get('protected', False)
                    project.variables.create(variable_data)

                    print(f"Variable '{key}' added successfully to project '{namespace}/{project_name}'.")
                else:
                    print(f"Variable '{key}' already exists in project '{namespace}/{project_name}'.")
            return True

        except gitlab.exceptions.GitlabCreateError as err:
            print(f"Failed to add variables: {err}")
            return False
        
    def lock_branch(self, namespace, project_name, branch):
        """
        Lock the branch
        """
        project = self.get_project(namespace, project_name)
        branch = project.branches.get(branch)
        branch.protect()

    def run_pipeline(self, namespace, project, branch, trigger='Accelerator', parameters=None):
        """
        Run the pipeline
        """
        trigger = self.get_or_create_trigger(namespace, project, trigger)
        project = self.get_project(namespace, project)
        pipeline = project.trigger_pipeline(ref=branch, token=trigger.token, variables=parameters)
        print(f"Pipeline triggered: {pipeline.web_url}")

    def get_trigger_list(self, namespace, project_name):
        """
        Get the trigger list
        """
        project = self.get_project(namespace, project_name)
        return project.triggers.list()

    def get_or_create_trigger(self, namespace, project_name, trigger_description):
        """
        Create the trigger
        """
        project = self.get_project(namespace, project_name)
        for t in project.triggers.list():
            if t.description == trigger_description:
                return t
        return project.triggers.create({'description': trigger_description})

    def merge_mr(self, namespace, project_name, mr_id):
        """
        Merge the MR
        """
        project = self.get_project(namespace, project_name)
        mr = project.mergerequests.get(mr_id)
        mr.merge()
        print(f"MR merged: {mr.web_url}")


if __name__ == '__main__':
    # Example usage for adding multiple variables
    pass
