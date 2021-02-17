import datetime
import fnmatch
import os
import tempfile
import time

from go-publish.db_models import PublishedFile
from go-publish.utils import get_celery_tasks

import dateutil.parser

from flask import current_app

from tzlocal import get_localzone

import yaml


class Repo():

    def __init__(self, local_path, conf):

        self.local_path = local_path  # No trailing slash

        perms = self._check_perms()
        if not perms['writable']:
            raise ValueError("Path '%s' is not writable" % local_path)

        self.conf = conf

        self.has_baricadr = False
        if current_app.baricadr_enabled and 'has_baricadr' in conf and conf['has_baricadr'] is True:
            self.has_baricadr = True

    def is_in_repo(self, path):
        path = os.path.join(path, "")

        return path.startswith(os.path.join(self.local_path, ""))

    def check_publish_file(self, new_file_path, version=1):
        # Run checks here : File exists, File does not exists already in this version in repo
        # Can we check if someone is writing in it?
        pass

    def publish_file(self, new_file_path, version=1):
        # Send task to copy file
        # (Copy file, create symlink, create PublishedFile entity?)
        # Maybe create file entity now to get UID? Or maybe not
        pass

    def list_files(self):
        # Maybe list all files registered in repos?
        files = PublishedFile.query.filter(PublishedFile.repo_path=self.local_path)
        return files

    def relative_path(self, path):
        return path[len(self.local_path) + 1:]

class Repos():

    def __init__(self, config_file):

        self.config_file = config_file

        self.read_conf(config_file)

    def read_conf(self, path):

        with open(path, 'r') as stream:
            self.repos = self.do_read_conf(stream.read())

    def read_conf_from_str(self, content):

        self.repos = self.do_read_conf(content)

    def do_read_conf(self, content):

        repos = {}
        repos_conf = yaml.safe_load(content)
        if not repos_conf:
            raise ValueError("Malformed repository definition '%s'" % content)

        for repo in repos_conf:
            # We use realpath instead of abspath to resolve symlinks and be sure the user is not doing strange things
            repo_abs = os.path.realpath(repo)
            if not os.path.exists(repo_abs):
                current_app.logger.warning("Directory '%s' does not exist, creating it" % repo_abs)
                os.makedirs(repo_abs)
            if repo_abs in repos:
                raise ValueError('Could not load duplicate repository for path "%s"' % repo_abs)

            for known in repos:
                if self._is_subdir_of(repo_abs, known):
                    raise ValueError('Could not load repository for path "%s", conflicting with "%s"' % (repo_abs, known))

            repos[repo_abs] = Repo(repo_abs, repos_conf[repo])

        return repos

    def _is_subdir_of(self, path1, path2):

        path1 = os.path.join(path1, "")
        path2 = os.path.join(path2, "")

        if path1 == path2:
            return True

        if len(path1) > len(path2):
            if path2 == path1[:len(path2)]:
                return True
        elif len(path1) < len(path2):
            if path1 == path2[:len(path1)]:
                return True

        return False

    def get_repo(self, path):

        path = os.path.join(path, "")

        for repo in self.repos:
            if self.repos[repo].is_in_repo(path):
                return self.repos[repo]

        raise RuntimeError('Could not find go-publish repository for path "%s"' % path)
