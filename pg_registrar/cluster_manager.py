import json
import os
from connection_manager import ConnectionManager
from logging_manager import LoggingManager


class ClusterManager:

    pg_cluster_json_path = os.getenv("PG_CLUSTER_JSON_PATH")
    pg_cluster_json = None
    cm = ConnectionManager()
    cluster_list = pg_cluster_json_path + "/pg_cluster.json"
    cluster_names = None
    _pg_cluster_count = 0

    @property
    def pg_cluster_count(self):
        return self._pg_cluster_count

    @property
    def pg_cluster_names(self):
        return self.pg_cluster_names

    def get_postgres_cluster_info(self):
        primary_label = 'postgres-operator.crunchydata.com/role=master'
        cluster_label = 'postgres-operator.crunchydata.com/cluster'
        labels = primary_label
        kube = self.cm.connect_to_kubernetes()
        ns = os.getenv("NAMESPACE")
        primary_pods = kube.list_namespaced_pod(namespace=ns,
                                                label_selector=labels)

        self._pg_cluster_count = 0
        self._pg_cluster_count = len(primary_pods.items)

        msg = '{count} postgres clusters detected in {namespace} ' \
            'namespace.'.format(count=self._pg_cluster_count,
                                namespace=ns)
        LoggingManager.logger.info(msg)

        self.cluster_names = []
        for pod in primary_pods.items:
            self.cluster_names.append(pod.metadata.labels[cluster_label])

    def create_postgres_cluster_json(self):
        pgadmin_cluster_info = {}
        count = 0
        pgadmin_server = {}
        ns = os.getenv("NAMESPACE")
        shared = bool(os.getenv('SHARED_SERVER'))
        port = int(os.getenv("POSTGRES_SERVICE_PORT"))
        sslmode = os.getenv('SSLMODE')

        for cluster_name in self.cluster_names:
            count += 1
            pg_cluster_info = {}
            pg_cluster_info["Name"] = cluster_name
            pg_cluster_info["Group"] = "Servers"
            pg_cluster_info["Port"] = port
            pg_cluster_info["Username"] = cluster_name
            pg_cluster_info["Host"] = cluster_name + "-ha." + ns + ".svc"
            pg_cluster_info["SSLMode"] = sslmode
            pg_cluster_info["MaintenanceDB"] = "postgres"
            pg_cluster_info["Shared"] = shared

            pgadmin_server[str(count)] = pg_cluster_info

        pgadmin_cluster_info["Servers"] = pgadmin_server
        pg_cluster_json = json.dumps(pgadmin_cluster_info, indent=4)

        LoggingManager.logger.debug("pg_cluster_json contents:")
        LoggingManager.logger.debug(pg_cluster_json)

        # self.cluster_list = self.pg_cluster_json_path + "/pg_cluster.json"
        with open(self.cluster_list, "w") as outfile:
            outfile.write(pg_cluster_json)

        msg = "Created pg_cluster.json in the {path} directory.".format(
            path=self.pg_cluster_json_path)
        LoggingManager.logger.info(msg)

    def create_empty_cluster_json(self):
        empty_cluster_info = {}
        empty_cluster_info["Servers"] = {}

        empty_cluster_json = json.dumps(empty_cluster_info, indent=4)

        empty_cluster_list = self.pg_cluster_json_path +\
            "/empty_pg_cluster.json"
        with open(empty_cluster_list, "w") as outfile:
            outfile.write(empty_cluster_json)

    def remove_pg_cluster_json(self):
        if os.path.exists(self.cluster_list):
            os.remove(self.cluster_list)
            LoggingManager.logger.debug("Deleted: {file}"
                                        .format(file=self.cluster_list))
