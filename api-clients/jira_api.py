
from jira import JIRA

from config_manager import ConfigManager

class JiraAPI:

    config = ConfigManager()
    def __init__(self):
        self.username = self.config['jira']['username']
        self.password = self.config['jira']['password'].encode()
        self.host = self.config['jira']['host']
        self.jira = JIRA(server=self.host, basic_auth=(self.username, self.password))

    def login(self):
        return self.jira

    def create_issue(self, project, summary, description, issuetype):
        return self.jira.create_issue(project=project, summary=summary, description=description, issuetype=issuetype)

    def get_issue(self, issue_id):
        return self.jira.issue(issue_id)

    def update_issue(self, issue_id, field, value, append=False):
        issue = self.jira.issue(issue_id)
        if append:
            print(value)
            existing_value = getattr(issue.fields, field)
            new_value = existing_value + "\n\n" + value.replace("\\n", "\n")
            issue.update(fields={field: new_value})
            print(f"issue {issue_id} updated")
        else:
            issue.update(fields={field: value})
            print(f"issue {issue_id} updated")

    def get_issue_transitions(self, issue):
        return self.jira.transitions(issue)

    def transition_issue(self, issue_id, transition):
        """
        User will select string not id
        """
        issue = self.get_issue(issue_id)
        transitions = self.get_issue_transitions(issue)
        transition_id = None
        for t in transitions:
            if t['name'] == transition:
                transition_id = t['id']
                break

        if transition_id:
            self.jira.transition_issue(issue, transition_id)
            print(f"issue {issue.key} transitioned to {transition}")
        else:
            print(f"transition {transition} not found")

    def get_latest_issue(self, project):
        return self.jira.search_issues(f'project={project} order by created DESC', maxResults=1)[0]

    def get_latest_issues(self, project, maxResults):
        return self.jira.search_issues(f'project={project} order by created DESC', maxResults=maxResults)







if __name__ == '__main__':

    jira = JiraAPI()
    # me = jira.login().myself()
