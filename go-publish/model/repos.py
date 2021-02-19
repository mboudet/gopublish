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
        self.conf = conf

        if not "public_folder" in conf or not conf["public_folder"]:
            raise ValueError("public_folder for path '%s' is either not set or empty" % local_path)
        if not os.path.isdir(conf["public_folder"]):
            raise ValueError("public_folder %s for path '%s' does not exists" % (conf["public_folder"], local_path))

        self.public_folder = conf["public_folder"]

        perms = self._check_perms()
        if not perms['writable']:
            raise ValueError("Path '%s' is not writable" % self.public_folder)

        self.has_baricadr = False
        if current_app.baricadr_enabled and 'has_baricadr' in conf and conf['has_baricadr'] is True:
            self.has_baricadr = True

    def is_in_repo(self, path):
        path = os.path.join(path, "")

        return path.startswith(os.path.join(self.local_path, ""))

    def check_publish_file(self, file_path, version=1):
        # Run checks here : File exists in that version
        # Can we check if someone is writing in it?
        # TODO : Check file exists, and file in repo
        if not os.path.exists(file_path)
            return {"available": False, "error": "Target file does not exists"}
        file_name = os.path.basename(file_path)
        name, ext = os.path.splitext(file_name)
        new_file_name = "{}_v{}{}".format(name, version, ext)
        if os.path.exists(os.path.join(self.public_folder, new_file_name))
            return {"available": False, "error": "File is already published in that version"}
        return {"available": True, "error": ""}

    def publish_file(self, file_path, version=1):
        # Send task to copy file
        # (Copy file, create symlink, create PublishedFile entity?)
        # Maybe create file entity now to get UID? Or maybe not
        file_name = os.path.basename(file_path)
        name, ext = os.path.splitext(file_name)
        new_file_path = os.path.join(self.public_folder, "{}_v{}{}".format(name, version, ext))

        pf = PublishedFile(file_path=new_file_path, old_file_path=file_path, repo_path=self.local_path)
        db.session.add(pf)
        db.session.commit()
        task = current_app.celery.send_task("publish"", (pf.id))


    def list_files(self):
        # Maybe list all files registered in repos?
        files = PublishedFile.query.filter(PublishedFile.repo_path=self.local_path)
        return files

    def relative_path(self, path):
        return path[len(self.local_path) + 1:]


    def _check_perms(self):
        if not current_app.is_worker:
            # The web app doesn't need to have write access, nor to check if the repo is freezable
            # The web forker thread is "nginx", not root, so it cannot write anyway.
            current_app.logger.debug("Web process, skipping perms checks for repo %s" % (self.public_folder))
            return {"writable": True}

        perms = {"writable": True}
        try:
            # Sometimes tmp file can escape their deletion: I guess it comes from multiple live code reload in dev mode
            with tempfile.NamedTemporaryFile(dir=self.public_folder) as test_file:
                starting_atime = os.stat(test_file.name).st_atime
                test_file.read()
        except OSError as err:
            current_app.logger.error("Got error while checking perms on %s: %s" % (self.public_folder, err))
            perms["writable"] = False

        current_app.logger.info("Worker process, perms detected for repo %s: %s" % (self.public_folder, perms))

        return perms

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
