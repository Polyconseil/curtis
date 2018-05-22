import urllib.parse as urlparse

import requests

from . import models
from . import utils


def get_full_url(cfg, path_or_url):
    if path_or_url.startswith('http'):
        return path_or_url
    else:
        base_url = urlparse.urljoin(cfg.url, '/api/0/')
        return urlparse.urljoin(base_url, path_or_url)


def get(cfg, path_or_url, params=None):
    return requests.get(
        get_full_url(cfg, path_or_url),
        auth=utils.auth_token(cfg.token),
        params=params,
        timeout=cfg.timeout,
    )


def put(cfg, path_or_url, data, params=None):
    full_url = get_full_url(cfg, path_or_url)
    response = requests.put(
        full_url,
        json=data,
        auth=utils.auth_token(cfg.token),
        timeout=cfg.timeout,
    )

    if response.status_code == 401:
        response = requests.put(
            full_url,
            json=data,
            auth=utils.auth_token(cfg.token),
            timeout=cfg.timeout,
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': response.cookies['sc'],
                'referer': full_url,
            },
            cookies=response.cookies,
            params=params,
        )

    return response


def delete(cfg, path_or_url):
    full_url = get_full_url(cfg, path_or_url)
    response = requests.delete(
        full_url,
        auth=utils.auth_token(cfg.token),
        timeout=cfg.timeout,
        headers={
            'Content-Type': 'application/json',
            'referer': full_url,
        },
    )

    if response.status_code != 200:
        response = requests.delete(
            full_url,
            auth=utils.auth_token(cfg.token),
            timeout=cfg.timeout,
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': response.cookies['sc'],
                'referer': full_url,
            },
            cookies=response.cookies,
        )

    return response


def page_iterator(cfg, url, params=None):
    next_url = url
    while next_url:
        response = get(cfg, next_url, params=params)
        next_url = response.links['next']['url'] if response.links.get('next', {'results': False})['results'] else None
        items = response.json()

        if not items:
            break

        for item in items:
            yield item


def organization_iterator(cfg):
    return page_iterator(cfg, 'organizations/')


def project_iterator(cfg, organization):
    url = 'organizations/{organization[slug]}/projects/'.format(
        organization=organization
    )
    return page_iterator(cfg, url)


def issue_iterator(cfg, organization, project, **params):
    already_seen_issues = set()
    url = 'projects/{organization[slug]}/{project[slug]}/issues/'.format(
        organization=organization,
        project=project,
    )
    issues = page_iterator(cfg, url, params=params)
    for issue in issues:
        if issue['id'] not in already_seen_issues:
            yield models.SentryIssue(organization, project, issue)
        already_seen_issues.add(issue['id'])


def opi_iterator(cfg, **params):
    for organization in organization_iterator(cfg):
        for project in project_iterator(cfg, organization):
            for issue in issue_iterator(cfg, organization, project, **params):
                yield issue


def mark_as_seen(cfg, issue):
    return put(
        cfg,
        'issues/{issue[id]}/'.format(issue=issue),
        {'hasSeen': True},
    )


def merge_issues(cfg, issues):
    issue = issues[0]
    return put(
        cfg,
        'projects/{organization}/{project}/issues/'.format(
            organization=issue.organization['slug'],
            project=issue.project['slug'],
        ),
        {'merge': 1},
        params={'id': [issue['id'] for issue in issues]},
    )


def resolve_issue(cfg, issue):
    return put(
        cfg,
        'issues/{issue[id]}/'.format(issue=issue),
        {'status': 'resolved'},
    )


def delete_issue(cfg, issue):
    return delete(
        cfg,
        'issues/{issue[id]}/'.format(issue=issue),
    )
