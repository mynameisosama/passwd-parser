"""
The following python script correlates data between user and groups of a linux system
"""
import os
import json
import logging
import argparse


DEFAULT_PASSWD_FILE = "/etc/passwd"
DEFAULT_GROUPS_FILE = "/etc/group"


class FormatError(Exception):
    """
    Define a custom error class for file formats
    """
    pass


def parse_group_data(_file):
    """
    Parse each line present in group file and return parameters
    :param _file: file pointer to read
    :return: name, group id, users
    """
    while True:
        _data = _file.readline()
        if not _data:
            break
        try:
            _d = _data.split(':')
            yield _d[0], _d[2], _d[3][:-1].split(',')
        except IndexError:
            raise FormatError("Invalid Format for Groups File")


def parse_user_data(_file):
    """
    Parse each line present in passwd file and return parameters
    :param _file: file pointer to read
    :return: name, user id, group id, description
    """
    while True:
        _data = _file.readline()
        if not _data:
            break
        try:
            _d = _data.split(':')
            yield _d[0], _d[2], _d[3], _d[4]
        except IndexError:
            raise FormatError("Invalid Format for Passwd File")


def parse_user_file(_file, _groups_by_id, _users):
    """
    Parse user file and populate users dictionary
    :param _file: path to passwd file
    :param _groups_by_id: dictionary of groups keyed by respective id
    :param _users: dictionary of users keyed by username
    """
    try:
        with open(_file) as _fp:
            # extract parameters from each line
            for u_name, u_uid, u_gid, u_info in parse_user_data(_fp):
                # check if extracted group id has an associated group present
                if u_gid in _groups_by_id:
                    # add group if its not the same as username
                    # by default each user has a group with the same name
                    if u_name != _groups_by_id[u_gid]:
                        _users[u_name] = {
                            'uid': u_uid,
                            'full_name': u_info,
                            'groups': [_groups_by_id[u_gid]]
                        }
                    else:
                        _users[u_name] = {
                            'uid': u_uid,
                            'full_name': u_info,
                            'groups': list()
                        }
                # incase a user is found whose group id
                # does not have asscoiated group
                else:
                    _users[u_name] = {
                        'uid': u_uid,
                        'full_name': u_info,
                        'groups': list()
                    }
    except(KeyError, IndexError, IOError) as exc:
        raise exc


def parse_group_file(_file, _groups_by_id, _groups_by_user):
    """
    Parse group file and populate users groups_by_id and groups_by_user
    :param _file: path to group file
    :param _groups_by_id: dictionary of groups keyed by respective id
    :param _groups_by_user: dictionary of groups keyed by username
    """
    try:
        with open(_file) as _fp:
            # extract parameters from each line
            for g_name, g_id, g_users in parse_group_data(_fp):
                # make link between user to group instaed of group to user
                for user in g_users:
                    if user in _groups_by_user:
                        _groups_by_user[user].append(g_name)
                    else:
                        _groups_by_user[user] = [g_name]
                # make association between group name and id
                _groups_by_id[g_id] = g_name
    except(KeyError, IndexError, IOError) as exc:
        raise exc


def correlate_users_groups(_users, _groups_by_user):
    """
    Iterate through user dictionary and populate groups of each user
    :param _users: dictionary of users keyed by username
    :param _groups_by_user: dictionary of groups keyed by username
    """
    try:
        for user in _users:
            if user in _groups_by_user:
                _users[user]['groups'].extend(_groups_by_user[user])
    except(KeyError, IndexError) as exc:
        raise exc


# Argument Parser
parser = argparse.ArgumentParser(
    description="combine and correlate user and group data"
)
parser.add_argument(
    "-p", "--passwd", type=str,
    help="path to passwords file, default=/etc/passwd",
    default=DEFAULT_PASSWD_FILE
)
parser.add_argument(
    "-g", "--groups", type=str,
    help="path to groups file, default=/etc/group",
    default=DEFAULT_GROUPS_FILE
)
args = parser.parse_args()
try:
    # Setup Logging
    path = os.path.dirname(os.path.abspath(__file__))
    logging.basicConfig(
        filename="%s/errors.log" % path, level=logging.ERROR,
        format="%(asctime)s %(message)s"
    )
    users = dict()
    groups_by_user = dict()
    groups_by_id = dict()
    parse_group_file(args.groups, groups_by_id, groups_by_user)
    parse_user_file(args.passwd, groups_by_id, users)
    correlate_users_groups(users, groups_by_user)
    # Print output to stdout
    print json.dumps(users, indent=4)
except(KeyError, IndexError, FormatError, IOError) as exc:
    logging.exception(exc)
