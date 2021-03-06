# -*- coding: utf-8 -*-


# GitDeploy -- Deploy git repositories to multiple targets.
# By: Christophe Benz <cbenz@easter-eggs.com>
#
# Copyright (C) 2013 Christophe Benz, Easter-eggs
# https://github.com/cbenz/git-deploy
#
# This file is part of GitDeploy.
#
# GitDeploy is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# GitDeploy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import glob
import json
import logging
import os

from . import conv


log = logging.getLogger(__name__)


def get_conf(config_dir_path):
    if not os.path.isdir(config_dir_path):
        return None
    conf_dicts = []
    for config_file_path in glob.iglob(os.path.join(config_dir_path, '*.json')):
        log.debug(u'config_file_path = {path}'.format(path=config_file_path))
        with open(config_file_path) as config_file:
            config_file_str = config_file.read()
        try:
            conf_dict = json.loads(config_file_str)
        except ValueError, exc:
            log.error(u'Failed to decode repository JSON configuration for file "{path}": {exc}'.format(
                exc=unicode(exc), path=config_file_path))
            return None
        conf_data, errors = conv.json_values_to_conf(conf_dict)
        if errors is not None:
            log.error(u'Repository configuration errors for file "{path}": {errors}'.format(
                errors=errors, path=config_file_path))
            return None
        conf_dicts.append(conf_data)
    conf = merge_conf_dicts(conf_dicts)
    log.debug(u'conf = {conf}'.format(conf=conf))
    return conf


def get_repo_alias_and_conf(conf, repo_url):
    if conf['repositories']:
        for repo_alias, repo_conf in conf['repositories'].iteritems():
            if repo_conf['url'] == repo_url:
                log.debug(u'repo_alias = {repo}, repo_conf = {conf}'.format(conf=repo_conf, repo=repo_alias))
                return repo_alias, repo_conf
    return None, None


def merge_conf_dicts(conf_dicts):
    hooks = {}
    repositories = {}
    for conf_dict in conf_dicts:
        if conf_dict.get('hooks'):
            hooks.update(conf_dict['hooks'])
        if conf_dict.get('repositories'):
            repositories.update(conf_dict['repositories'])
    return {'hooks': hooks, 'repositories': repositories}
