#!/usr/bin/env python
import collections
import functools
import webbrowser

import click
import requests
import termcolor

from . import client
from . import config
from . import filters
from . import output
from . import utils

DEFAULT_AGE_OF_ISSUES_TO_RESOLVE = 30  # days
DEFAULT_AGE_OF_ISSUES_TO_MARK_AS_SEEN = 7  # days


def with_title_filtering(fun):
    @functools.wraps(fun)
    @click.option(
        '--include',
        '-f',
        multiple=True,
        help="Patterns of issue titles to include (Python regular expression)",
    )
    @click.option(
        '--exclude',
        '-e',
        multiple=True,
        help="Patterns of issue titles to exclude (Python regular expression)",
    )
    def decorated(*args, **kwargs):
        return fun(*args, **kwargs)

    return decorated


@click.group()
@click.option('--config-file', type=click.Path(exists=True))
@click.option('--site', default=None)
@click.pass_context
def main(ctx, config_file=None, site=None):
    cfg = config.load_config(config_file, site)
    ctx.obj = cfg


@main.command(name='assigned-issues')
@click.pass_obj
def assigned_issues(cfg):
    """Show assigned issues"""
    issues = client.opi_iterator(cfg, query='is:unresolved is:assigned')
    for line, _issue in output.tree_shaped(cfg, issues):
        print(line)


@main.command(name='assigned-issues-by-assignee')
@click.pass_obj
def assigned_issues_by_assignee(cfg):
    """Show issues by assignee"""
    issues = client.opi_iterator(cfg, query='is:unresolved is:assigned')

    # build Assignee -> issues table
    assigned = collections.defaultdict(list)
    for issue in issues:
        print('.', end='', flush=True)
        assigned[issue['assignedTo']['username']].append(issue)
    print()

    for assignee, issues in assigned.items():
        print('- {}'.format(assignee))
        for issue in issues:
            print('  - {}'.format(output.shaped_issue(cfg, issue)))


@main.command(name='browse-unseen-issues')
@click.option(
    '--age',
    default=DEFAULT_AGE_OF_ISSUES_TO_MARK_AS_SEEN,
    help="Age (in days) of to check",
    show_default=True,
)
@with_title_filtering
@click.pass_obj
def browse_unseen_issues(cfg, age, include, exclude):
    """Browse unseen issues"""
    batch_size = 10
    msg_tpl = "Opening {} preceding unseen issues in browser? [Y/n | ^C to quit]"

    issues = client.opi_iterator(cfg, query='is:unresolved is:unassigned')
    issues = filters.unseen(filters.max_age(issues, days=age))
    issues = filters.filter_title(issues, include, exclude)

    for issues in utils.grouper(output.tree_shaped(cfg, issues), batch_size):
        print('-' * 120)
        for line, issue in issues:
            print(line)

        confirmation = utils.confirm(msg_tpl.format(len(issues)), 'yn', default='n')
        if confirmation == 'y':
            for _line, item in issues:
                if item:
                    webbrowser.open_new_tab(item.issue['permalink'])


@main.command(name='check-trends')
@click.option(
    '--period',
    default='12h',  # FIXME: constant
    help="""Time period to compute trend stats""",
    show_default=True,
)
@click.option(
    '--threshold',
    default=1,  # FIXME: constant
    type=click.FLOAT,
    help="Issues with a trend ratio below this threshold are ignored",
    show_default=True,
)
@with_title_filtering
@click.pass_obj
def check_trends(cfg, period, threshold, include, exclude):
    """Show evolution stats for seen issues"""
    stats_period, days, hours = utils.decode_period(period)

    issues = client.opi_iterator(cfg, query='is:unresolved is:unassigned', statsPeriod=stats_period)
    issues = filters.max_age(filters.seen(issues), days=days, hours=hours)
    issues = filters.filter_title(issues, include, exclude)

    for line, issue in output.tree_shaped(cfg, issues):
        if not issue:
            print(line)
            continue

        level, ratio, count = utils.compute_events_stats(
            stats_period,
            days or hours,
            threshold,
            issue,
        )

        if level < 1:  # Don't bother with issue
            continue

        print(
            line,
            '\n   ',
            termcolor.colored(
                'New in period' if not ratio else 'Ratio {ratio:.01f}'.format(ratio=ratio),
                color='magenta' if not ratio else ('red' if level == 2 else 'yellow'),
            ),
            termcolor.colored(
                '({count} new occurence(s)'.format(count=count),
                color='white', attrs=['bold']
            )
        )


@main.command(name='mark-as-seen')
@click.option(
    '--age',
    default=DEFAULT_AGE_OF_ISSUES_TO_MARK_AS_SEEN,
    help="Age (in days) of entries to mark seen",
    show_default=True,
)
@click.pass_obj
def mark_seen(cfg, age):
    """Mark issues as seen"""
    issues = client.opi_iterator(cfg, query='is:unresolved is:unassigned')
    issues = filters.unseen(filters.outdated(issues, age))
    for line, issue in output.tree_shaped(cfg, issues):
        line, _issue = utils.run_command(client.mark_as_seen, cfg, issue, line)
        print(line)


@main.command(name='merge-issues')
@click.pass_obj
def merge_issues(cfg):
    """Merge related issues together"""
    groups = collections.defaultdict(list)

    # Collect issues and group them
    issues = client.opi_iterator(cfg)
    for line, issue in output.tree_shaped(cfg, issues):
        if issue:
            key = (
                issue['project']['slug'],
                issue['metadata'].get('type'),
                issue['metadata'].get('value'),
                issue['metadata'].get('title'),
                issue['culprit'],
            )
            groups[key].append(issue)
        print(line)

    # Merge issues
    for issues in groups.values():
        if len(issues) <= 1:
            continue

        project = issues[0].project['slug']
        print(project, ':: merging issues: ', [issue['id'] for issue in issues])
        try:
            client.merge_issues(cfg, issues)
        except requests.exceptions.ConnectionError as e:
            print('ERROR, %s' % e)


@main.command(name='needs-triage')
@click.pass_obj
def needs_triage(cfg):
    """Show issues than needs triage"""
    issues = client.opi_iterator(cfg, query='is:unresolved is:unassigned')
    for line, _issue in output.tree_shaped(cfg, issues):
        print(line)


@main.command(name='resolve-issues')
@click.option(
    '--age',
    default=DEFAULT_AGE_OF_ISSUES_TO_RESOLVE,
    help='Age (in days) of entries to resolve',
    show_default=True,
)
@click.pass_obj
def resolve_issues(cfg, age):
    """Resolve outdated issues"""
    issues = client.opi_iterator(cfg, query='is:unresolved is:unassigned')
    issues = filters.outdated(issues, days=age)
    for line, issue in output.tree_shaped(cfg, issues):
        line, _issue = utils.run_command(client.resolve_issue, cfg, issue, line)
        print(line)


@main.command(name='remove-issues')
@click.option(
    '--age',
    default=DEFAULT_AGE_OF_ISSUES_TO_RESOLVE,
    help='Age (in days) of entries to remove',
    show_default=True,
)
@click.pass_obj
def remove_issues(cfg, age):
    """
    Remove outdated issues.

    No action is performed on commented or assigned issues.
    """
    issues = client.opi_iterator(cfg, query='is:unresolved is:unassigned')
    issues = filters.outdated(issues, days=age)
    for line, issue in output.tree_shaped(cfg, issues):
        # Preserve issue with comment (None issue is for display purpose)
        if issue is not None and issue.numComments == 0:
            line, _issue = utils.run_command(client.delete_issue, cfg, issue, line)
        print(line)


if __name__ == '__main__.py':
    main()
