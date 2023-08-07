from kubernetes import client, config
from logging_manager import LoggingManager


class ConnectionManager:
    """Opens and closes Kubernetes cluster connections
    """

    lm = LoggingManager()

    def __init__(self):
        if not hasattr(ConnectionManager, 'kubernetes_connection'):
            ConnectionManager.kubernetes_connection = \
                self.connect_to_kubernetes()

    def connect_to_kubernetes(self):
        """Connects to the Kubernetes cluster that the container is running in.
        """

        LoggingManager.logger.debug("Connecting to kubernetes.")
        # config.load_kube_config("/Users/robertpacheco/.kube/config")
        config.load_incluster_config()
        self.kube = client.CoreV1Api()

        return self.kube

    def close_kubernetes_connection(self):
        """Closes the connection to the Kubernetes cluster
        """
        ConnectionManager.kubernetes_connection.api_client.close()
        ConnectionManager.kubernetes_connection.api_client = None
        LoggingManager.logger.debug("Closed kubernetes connection.")
