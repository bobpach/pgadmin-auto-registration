import os
import time
from logging_manager import LoggingManager
from cluster_manager import ClusterManager
from config_manager import ConfigManager
from connection_manager import ConnectionManager
from kubernetes.stream import stream


class RegistrationManager:

    # init supporting objects
    loggingManager = LoggingManager()
    configManager = ConfigManager()
    connectionManager = ConnectionManager()
    clusterManager = ClusterManager()

    def register_postgres_clusters(self):

        try:
            LoggingManager.logger.debug("Started")
            self.clusterManager.get_postgres_cluster_info()
            if self.clusterManager.pg_cluster_count > 0:
                self.clusterManager.create_postgres_cluster_json()
                self.execute_postgres_registration()
            else:
                self.clusterManager.remove_pg_cluster_json()
                # self.clusterManager.create_empty_cluster_json()
                # self.execute_postgres_registration(True)
        except (Exception) as error:
            LoggingManager.logger.error(error, exc_info=True)

    def execute_postgres_registration(self, empty=False):
        try:
            ns = os.getenv("NAMESPACE")
            exec_command = ['sh']
            label = "app=pgadmin"
            kube = ConnectionManager.kubernetes_connection

            pgadmin_pods = kube.list_namespaced_pod(namespace=ns,
                                                    label_selector=label)

            pod_count = len(pgadmin_pods.items)
            msg = '{count} pgadmin pods found in {namespace} ' \
                'namespace.'.format(count=pod_count,
                                    namespace=ns)
            LoggingManager.logger.info(msg)

            for pod in pgadmin_pods.items:
                pgadmin_pod_name = pod.metadata.name

            LoggingManager.logger.debug("PGAdmin pod name: {pod_name}"
                                        .format(pod_name=pgadmin_pod_name))
            LoggingManager.logger.debug("Namespace: {namespace}"
                                        .format(namespace=ns))
            LoggingManager.logger.debug("exec_command: {command}"
                                        .format(command=exec_command))

            resp = stream(kube.connect_get_namespaced_pod_exec,
                          pgadmin_pod_name,
                          namespace=ns,
                          command=exec_command,
                          stderr=True, stdin=True,
                          stdout=True, tty=False,
                          container="pgadmin",
                          _preload_content=False)

            pgadmin_user = os.getenv('PGADMIN_USER')

            # set the command to use the correct json file
            if not empty:
                command = '/venv/bin/python3 /pgadmin4/setup.py'\
                          ' --load-servers'\
                          ' /var/lib/pgadmin/pg_cluster.json'\
                          ' --user="{user}" --replace'.format(
                              user=pgadmin_user)
            else:
                command = '/venv/bin/python3 /pgadmin4/setup.py'\
                          ' --load-servers'\
                          ' /var/lib/pgadmin/empty_pg_cluster.json'\
                          ' --user="{user}" --replace'.format(
                              user=pgadmin_user)

            LoggingManager.logger.debug("Command to be executed: {cmd}"
                                        .format(cmd=command))
            resp.write_stdin(command)
            resp.close()

        except (Exception) as error:
            LoggingManager.logger.error(error, exc_info=True)

    def cleanup(self):
        if self.connectionManager is not None:
            self.connectionManager.close_kubernetes_connection()
            self.connectionManager = None
        if self.loggingManager is not None:
            self.loggingManager.remove_handlers(LoggingManager.logger)
            self.loggingManager = None
        self.clusterManager = None
        self.configManager = None


# entry point
if __name__ == '__main__':
    try:
        rm = RegistrationManager()
        rm.register_postgres_clusters()
        while True:
            wait_interval = int(os.getenv('WAIT_INTERVAL_SECONDS'))
            time.sleep(wait_interval)
            rm.register_postgres_clusters()
    finally:
        rm.cleanup()
        rm = None
