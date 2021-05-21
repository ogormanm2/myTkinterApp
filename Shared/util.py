import json


def load_connection_defaults(path_to_json):
    with open(path_to_json, "r") as handler:
        info = json.load(handler)
    return info


def save_connection_defaults(user_name, host, port, db, path_to_json):
    profile = {"user": user_name, "host": host, "port": port, "db":  db}
    with open(path_to_json, 'w') as outfile:
        json.dump(profile, outfile, ensure_ascii=False, indent=4)


def unique(list1):
    unique_list = []
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list
