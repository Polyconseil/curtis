class SentryIssue(object):
    def __init__(self, organization, project, issue):
        self.organization = organization
        self.project = project
        self.issue = issue

    def __getitem__(self, key, default=None):
        return self.issue.get(key, default)

    def __getattr__(self, item):
        return self[item]
