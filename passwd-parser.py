import sys, traceback, json


DEFAULT_PASSWD_FILE = "/etc/passwd"
DEFAULT_GROUPS_FILE = "/etc/group"

class FormatError(Exception):
    pass


def read_by_line(_file):
    while(True):
        data = _file.readline()
        if(not data):
            break
        yield data


def parse_group_data(_data):
    _d = _data.split(':')
    try:
        return _d[0], _d[2], _d[3][:-1].split(',')
    except(IndexError) as e:
        raise FormatError("Invalid Format for Password File")


def parse_user_data(_data):
    _d = _data.split(':')
    try:
         return _d[0], _d[2], _d[3], _d[4]
    except(IndexError) as e:
        raise FormatError("Invalid Format for Groups File")


def parse_user_file(_file, groups_by_id, users):
    try:
        with open(_file) as f:
            for line in read_by_line(f):
                u_name, u_uid, u_gid, u_info = parse_user_data(line)
                if u_gid in groups_by_id:
                    if u_name != groups_by_id[u_gid]:
                        users[u_name] = {
                            'uid': u_uid,
                            'full_name': u_info,
                            'groups': [groups_by_id[u_gid]]
                        }
                    else:
                        users[u_name] = {
                            'uid': u_uid,
                            'full_name': u_info,
                            'groups': list()
                        }
    except(KeyError, IndexError, IOError) as e:
        raise(e)


def parse_group_file(_file, groups_by_id, groups_by_users):
    try:
        with open(_file) as f:
            for line in read_by_line(f):
                g_name, g_id, g_users = parse_group_data(line)
                for user in g_users:
                    if user in groups_by_user:
                        groups_by_user[user].append(g_name)
                    else:
                        groups_by_user[user] = [g_name]
                groups_by_id[g_id] = g_name
    except(KeyError, IndexError, IOError) as e:
        raise(e)


def correlate_users_groups(users, grousp_by_users):
    try:
        for user in users:
            if user in groups_by_user:
                users[user]['groups'].extend(groups_by_user[user])
    except(KeyError, IndexError) as e:
        raise(e)


try:
    passwd = sys.argv[1]
except(IndexError):
    passwd = DEFAULT_PASSWD_FILE
try:
    groups = sys.argv[2]
except(IndexError):
    groups = DEFAULT_GROUPS_FILE
try:
    users = dict()
    groups_by_user = dict()
    groups_by_id = dict()
    parse_group_file(groups, groups_by_id, groups_by_user)
    parse_user_file(passwd, groups_by_id, users)
    correlate_users_groups(users, groups_by_user)
    print(json.dumps(users, indent=4))
except(Exception):
    print(traceback.print_exc())

