import datetime
import functools
import re


def filter_regex_title(issues, regex):
    for issue in issues:
        if re.match(regex, issue.title):
            yield issue


def filter_title(issues, include, exclude):
    return functools.reduce(
        lambda filtered, regex: filter_regex_title(filtered, regex=regex),
        list(map(lambda exp: re.compile(r'^.*%s.*$' % exp), include)) +
        list(map(lambda exp: re.compile(r'^((?!%s).)*$' % exp), exclude)),
        issues,
    )


def outdated(issues, days):
    boundary = '{:%Y-%m-%dT%H:%M%S}Z'.format(datetime.datetime.utcnow() - datetime.timedelta(days=days))
    for issue in issues:
        if issue['lastSeen'] <= boundary:
            yield issue


def max_age(issues, days, hours=0):
    boundary = '{:%Y-%m-%dT%H:%M%S}Z'.format(datetime.datetime.utcnow() - datetime.timedelta(days=days, hours=hours))
    for issue in issues:
        if issue['lastSeen'] >= boundary:
            yield issue


def seen(issues):
    for issue in issues:
        if issue['hasSeen']:
            yield issue


def unseen(issues):
    for issue in issues:
        if not issue['hasSeen']:
            yield issue
