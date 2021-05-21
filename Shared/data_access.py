import psycopg2
from Shared import util


class DataAccess:

    def __init__(self, client_loads_list, clients, environments, message):
        self.__client_loads_list = client_loads_list
        self.__clients = clients
        self.__environments = environments
        self.__message = message
        self.__approval_control_id = 0
        self.__approved_flag = 0

    def get_client_loads_list(self):
        return self.__client_loads_list

    def get_clients(self):
        return self.__clients

    def set_clients(self, clients):
        self.__clients = clients

    def get_environments(self):
        return self.__environments

    def set_environments(self, environments):
        self.__environments = environments

    def get_message(self):
        return self.__message

    def set_message(self, message):
        self.__message = message

    def get_approval_control_id(self):
        return self.__approval_control_id

    def set_approval_control_id(self, approval_control_id):
        self.__approval_control_id = approval_control_id

    def get_approved_flag(self):
        return self.__approved_flag

    def set_approved_flag(self, approved_flag):
        self.__approved_flag = approved_flag

    def get_client_load_id_list(self, client):
        load_ids = ['']
        for sub in self.__client_loads_list:
            if sub['global_client_id'] == client:
                load_ids.append(sub['global_load_id'])
        return util.unique(load_ids)

    def get_client_load_version_list(self, client, load_id):
        load_versions = ['']
        for sub in self.__client_loads_list:
            if (sub['global_client_id'] == client) and (sub['global_load_id'] == load_id):
                load_versions.append(sub['global_load_version'])
        return util.unique(load_versions)

    def set_client_load_list(self, connection):
        try:
            connection.set_isolation_level(0)
            cur = connection.cursor()
            select_query = "SELECT * FROM cgtpp_config.card_approval_control;"
            cur.execute(select_query)
            records = cur.fetchall()
        except Exception as error:
            self.set_message("Query failed: " + str(error))
            return 1
        try:
            i = 0
            for row in records:
                self.__environments.append(row[1])
                self.__clients.append(row[2])
                self.__client_loads_list.append(
                    {"card_approval_control_id": row[0], "environment_tag": row[1], "global_client_id": row[2],
                     "global_load_id": row[3],
                     "global_load_version": row[4], "isaac_client_num": row[5], "approved_flag": row[6],
                     "approved_by": row[7]})
                i = i + 1
            connection.close()
            cur.close()
            self.__environments = util.unique(self.__environments)
            self.__clients = util.unique(self.__clients)
            return 0
        except Exception as error:
            self.set_message("Data set load failed: " + str(error))
            return 2

    def append_rows(self, connection, all_clients_flag, client_number):
        try:
            connection.set_isolation_level(0)
            cur = connection.cursor()

            select_query = "INSERT INTO cgtpp_config.card_approval_control (" + \
                           "global_client_id, environment_tag, global_load_id, global_load_version, isaac_client_num, approved_flag, approved_by)" + \
                           " SELECT DISTINCT CONCAT(SUBSTRING(a.client_id, 1, LENGTH(a.client_id)-1), '0')::INTEGER AS global_client_id," + \
                           " e.environment_tag as environment_tag, a.load_id as global_load_id, a.global_load_version, b.isaac_client_num," + \
                           " 0 AS approved_flag, NULL AS approved_by FROM cgtdwh.d_load_master a JOIN cgtdwh.d_client b on a.client_id = b.client_id and a.load_id>='2019Q1'"

            if all_clients_flag == 1:
                select_query = select_query + " AND CONCAT(SUBSTRING(a.client_id, 1, LENGTH(a.client_id)-1), '0')::INTEGER =" + str(
                    client_number)

            select_query = select_query + \
                           " CROSS JOIN (SELECT DISTINCT environment_tag FROM cgtpp_config.environment) e" + \
                           " WHERE NOT EXISTS (SELECT 1 FROM cgtpp_config.card_approval_control d INNER JOIN cgtpp_config.environment e" + \
                           " ON (d.environment_tag = e.environment_tag ) WHERE d.global_client_id = CONCAT(SUBSTRING(a.client_id, 1, LENGTH(a.client_id)-1), '0')" + \
                           " AND d.global_load_id = a.load_id AND d.global_load_version = a.global_load_version AND e.environment_tag = d.environment_tag)" + \
                           " ORDER BY a.client_id, a.load_id, a.global_load_version"

            cur.execute(select_query)
            #print(select_query)
            connection.close()
            cur.close()
            if all_clients_flag == 1:
                self.set_message("Rows loaded for all clients.")
            else:
                self.set_message("Rows loaded for client: [" + str(client_number) + "]")
            return 0
        except:
            return 1

    def approve_client_load(self, connection, approved_value, text_user_name, approval_key_entry, client, environment):
        try:
            connection.set_isolation_level(0)
            cur = connection.cursor()

            select_query = "UPDATE cgtpp_config.card_approval_control SET approved_flag=" + approved_value + ", approved_by='" + text_user_name + \
                           "' WHERE card_approval_control_id=" + approval_key_entry
            cur.execute(select_query)

            if approved_value == "1":
                self.set_message(
                    "Load approval enabled by " + text_user_name + " for row ID: [" + approval_key_entry + "]")
                select_query = "UPDATE cgtpp_config.card_approval_control SET approved_flag=0 WHERE card_approval_control_id !=" + approval_key_entry + \
                               " AND global_client_id = " + str(client) + " AND environment_tag = '" + environment + "'"
                cur.execute(select_query)
            else:
                self.set_message(
                    "Load approval disabled by " + text_user_name + " for row ID: [" + approval_key_entry + "]")

            connection.close()
            cur.close()

            # Update the in-memory dataset
            i = 0
            for sub in self.__client_loads_list:
                if str(sub['card_approval_control_id']) == str(approval_key_entry):
                    self.__client_loads_list[i]["approved_flag"] = int(approved_value)
                    self.__client_loads_list[i]["approved_by"] = text_user_name
                    break
                i = i + 1

            return 0
        except:
            return 1

    def select_result(self, environment, client, load_id, load_version):
        try:
            for sub in self.__client_loads_list:
                if (sub['environment_tag'] == environment and sub['global_client_id'] == client
                        and sub['global_load_id'] == load_id
                        and sub['global_load_version'] == load_version):
                    self.set_approval_control_id(sub['card_approval_control_id'])
                    environment_tag = sub['environment_tag']
                    gbl_client_id = str(sub['global_client_id'])
                    gbl_load_id = sub['global_load_id']
                    gbl_load_version = sub['global_load_version']
                    isaac_client_num = str(sub['isaac_client_num'])
                    self.set_approved_flag(sub['approved_flag'])
                    if sub['approved_by'] is None or len(sub['approved_by']) == 0:
                        approved_by = 'null'
                    else:
                        approved_by = sub['approved_by']
                    # Setup the card result row
                    self.set_message(
                        "         " + environment_tag + "          |          " + gbl_client_id + "           |           " + gbl_load_id +
                        "     |      " + gbl_load_version + "    |           " + isaac_client_num + "                   |          " + approved_by + "                ")
                    return 0
        except Exception as error:
            self.set_message("Data row select failed: " + str(error))
            return 1
