import os


class ConfigManager:

    def __init__(self):
        self.set_default_config_values()

    def set_default_config_values(self):
        """ Sets the default config values if not set in configmap
        """

        # defaults the log level to info
        if "LOG_LEVEL" not in os.environ:
            os.environ["LOG_LEVEL"] = "info"

        # defaults the log path to /pgadmin4
        if "LOG_PATH" not in os.environ:
            os.environ["LOG_PATH"] = "/pgadmin4"
            # os.environ["LOG_PATH"] = "."

        # defaults the json path to /pgadmin4
        if "PG_CLUSTER_JSON_PATH" not in os.environ:
            os.environ["PG_CLUSTER_JSON_PATH"] = "/pgadmin4"
            # os.environ["PG_CLUSTER_JSON_PATH"] = "."

        # defaults the postgres service port to 5432
        if "POSTGRES_SERVICE_PORT" not in os.environ:
            os.environ["POSTGRES_SERVICE_PORT"] = "5432"

        # defaults the shared server option to false
        if "SHARED_SERVER" not in os.environ:
            os.environ["SHARED_SERVER"] = "false"

        # defaults the SSL mode to prefer
        if "SSLMODE" not in os.environ:
            os.environ["SSLMODE"] = "prefer"

        # defaults the wait interval to 1 hour
        if "WAIT_INTERVAL_SECONDS" not in os.environ:
            os.environ["WAIT_INTERVAL_SECONDS"] = "3600"
            # os.environ["WAIT_INTERVAL_SECONDS"] = "30"

        if "NAMESPACE" not in os.environ:
            os.environ["NAMESPACE"] = "postgres-operator"
