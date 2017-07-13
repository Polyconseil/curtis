import configparser
import os.path


class CurtisConfig:
    CONFIG_PATHS = [
        './curtis.ini',
        '~/.curtis.ini',
    ]
    DEFAULT_TIMEOUT = 10
    SITE_PREFIX = 'site:'

    def __init__(self, config_file=None, site=None):
        self.parser = configparser.ConfigParser()
        self.parser.add_section('curtis')

        config_paths = [config_file] if config_file else self.CONFIG_PATHS
        for file_path in config_paths:
            file_path = os.path.expanduser(file_path)
            if os.path.exists(file_path):
                with open(file_path) as fp:
                    self.parser.read_file(fp)
                break

        self.site = site or self.default_site

    @property
    def sites(self):
        return sorted([
            name[len(self.SITE_PREFIX):]
            for name in self.parser.sections()
            if name.startswith(self.SITE_PREFIX)
        ])

    @property
    def default_site(self):
        return self.parser['curtis'].get('default_site') or self.sites[0]

    def _get_site_config(self, key, default=None):
        return self.parser['{}{}'.format(self.SITE_PREFIX, self.site)].get(key, default)

    @property
    def url(self):
        return self._get_site_config('url')

    @property
    def token(self):
        return self._get_site_config('token')

    @property
    def timeout(self):
        return self._get_site_config('timeout', self.DEFAULT_TIMEOUT)


def load_config(config_file, site):
    return CurtisConfig(config_file, site)
