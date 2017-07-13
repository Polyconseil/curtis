import datetime


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


def unseen(issues):
    for issue in issues:
        if not issue['hasSeen']:
            yield issue


def seen(issues):
    for issue in issues:
        if issue['hasSeen']:
            yield issue
