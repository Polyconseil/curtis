import termcolor

from . import utils


ISSUE_COLORS = {
    'fatal': 'red',
    'error': 'red',
    'warning': 'yellow',
    'info': 'blue',
    'debug': 'grey',
}


def shaped_project(cfg, project):
    return ' '.join([
        termcolor.colored('{project[slug]}'.format(project=project), color='cyan', attrs=['bold']),
        termcolor.colored('[{url}/sentry/{project[slug]}/]'.format(url=cfg.url, project=project), color='cyan'),
    ])


def shaped_issue(cfg, issue):
    color = ISSUE_COLORS[issue.level]
    assignee = (issue['assignedTo'] or {}).get('username', '')
    title = utils.stringify(issue.title)
    return ' '.join([
        termcolor.colored('{title}'.format(title=title), color=color, attrs=['bold']),
        termcolor.colored('{assignee}'.format(assignee=assignee), color='white'),
        termcolor.colored('{issue[lastSeen]} [{issue[permalink]}]'.format(issue=issue), color=color),
    ])


def tree_shaped(cfg, issues):
    current_project = None
    for issue in issues:
        if current_project != issue.project:
            current_project = issue.project
            yield '- {}'.format(shaped_project(cfg, issue.project)), None
        yield '  - {}'.format(shaped_issue(cfg, issue)), issue
