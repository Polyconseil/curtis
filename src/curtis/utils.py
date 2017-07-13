import re

import requests


SENTRY_STAT_PERIOD_DAY = '24h'
SENTRY_STAT_PERIOD_FORTNIGHT = '14d'


def auth_token(token):
    def inner(request):
        request.headers['Authorization'] = 'Basic {}'.format(token)
        return request
    return inner


def stringify(value):
    try:
        return str(value)
    except UnicodeEncodeError:
        return repr(value)


def run_command(fct, cfg, issue, line):
    if not issue:
        return line, issue

    try:
        fct(cfg, issue)
        return line, issue
    except requests.exceptions.ConnectionError as e:
        return '{} --> ERROR, {}'.format(line, e), issue


def grouper(iterable, n):
    """Collect data into fixed-length chunks or blocks"""
    block = []
    for index, item in enumerate(iterable, start=1):
        block.append(item)

        if index % n == 0:
            yield block
            block.clear()

    yield block


def confirm(message, accepted_values, default=None):
    confirmation = None
    while not confirmation or confirmation not in accepted_values:
        confirmation = input(message).lower() or default
    return confirmation


def decode_period(period):
    pattern = r'^(?P<value>\d+)(?P<unit>[hd])$'
    matched = re.search(pattern, period)
    if not matched:
        raise RuntimeError('Bad period format: %s, should be \d+(h|d).' % period)

    data = matched.groupdict()
    unit = data['unit']
    value = int(data['value'])

    assert unit == 'd' or value <= 12, '12h is the maximum available period.'
    assert unit == 'h' or value <= 7, '7d is the maximum available period.'

    return (
        SENTRY_STAT_PERIOD_DAY if unit == 'd' else SENTRY_STAT_PERIOD_FORTNIGHT,
        value if unit == 'd' else 0,
        value if unit == 'h' else 0,
    )


def compute_events_stats(stats_period, period_length, threshold, issue):
    occurrences = issue['stats'][stats_period]
    latest_index = 24 if stats_period == SENTRY_STAT_PERIOD_DAY else 12

    current_count = sum([occurrences[t][1] for t in range(latest_index - period_length, latest_index)])
    old_count = sum([
        occurrences[t][1] for t in range(latest_index - 2 * period_length, latest_index - period_length)
    ])

    ratio = current_count / old_count if old_count != 0 else None

    if ratio is None:
        level = 0 if current_count == 0 else 2
    elif ratio >= 2 * threshold:
        level = 2
    elif ratio >= threshold:
        level = 1
    else:
        level = 0

    return level, ratio, current_count
