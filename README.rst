Curtis - A simple sentry_ cli
=============================

.. _sentry: https://sentry.io


Configuration
-------------

Curtis configuration live in an INI file named ``curtis.ini`` in the
current directory or in the ``.curtis.ini`` in your home directory.

This file use the following format.

.. code-block:: ini

    [curtis]
    # define the default site
    default_site = foo

    # settings for the foo site
    [site:foo]
    # sentry server URL
    url = https://sentry.foo..example.com
    # sentry API token (this one is a fake one generated using the apg command)
    token = IvlayltajPamthelwaj1

    # settings for the bar site
    [site:bar]
    url = https://sentry.bar.example.org
    token = TeinkutbicyeckyoQuoa

Installation
------------

.. code-block:: console

    $ pip install curtis


Usage
-----

Once you have installed curtis and created a configuration file, you can use the curtis command

.. code-block:: console

    $ curtis --help
    Usage: curtis [OPTIONS] COMMAND [ARGS]...

    Options:
      --config-file PATH
      --site TEXT
      --help              Show this message and exit.

    Commands:
      assigned-issues              Show assigned issues
      assigned-issues-by-assignee  Show issues by assignee
      browse-unseen-issues         Browse unseen issues
      check-trends                 Show evolution stats for seen issues
      mark-as-seen                 Mark issues as seen
      merge-issues                 Merge related issues together
      needs-triage                 Show issues than needs triage
      resolve-issues               Resolve outdated issues

Each command have is one set of arguments use ``curtis <command> --help`` to display them.
