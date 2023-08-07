import json
# import os
# import time
from kubernetes import client, config
from kubernetes.stream import stream


class RegistrationManager:
    cluster_names = []
    # ns = os.getenv['NAMESPACE']
    ns = "postgres-dev"
    kube = None
    pg_cluster_json = None

    def register_postgres_clusters(self):
        self.connect_to_kubernetes_cluster()
        self.get_postgres_cluster_names()
        self.create_postgres_cluster_json()
        self.execute_postgres_registration()

    def execute_postgres_registration(self):
        exec_command = ['--it python3 /pgadmin4/setup.py /usr/lib/python3.8  --load-servers /var/lib/pgadmin/pg_cluster.json --replace']
        # exec_command = ['python3 /pgadmin4/setup.py']

        label = "app=pgadmin"
        pgadmin_pods = self.kube.list_namespaced_pod(namespace=self.ns,
                                                     label_selector=label)
        for pod in pgadmin_pods.items:
            pgadmin_pod_name = pod.metadata.name

        resp = stream(self.kube.connect_get_namespaced_pod_exec,
                      pgadmin_pod_name,
                      self.ns,
                      command=exec_command,
                      stderr=True, stdin=True,
                      stdout=True, tty=False,
                      _preload_content=False)

        print(resp)

    def create_postgres_cluster_json(self):
        pgadmin_cluster_info = {}
        count = 0
        pgadmin_server = {}
        for cluster_name in self.cluster_names:
            count += 1
            pg_cluster_info = {}
            pg_cluster_info["Name"] = cluster_name
            pg_cluster_info["Group"] = "Servers"
            pg_cluster_info["Port"] = "5432"
            pg_cluster_info["Username"] = cluster_name
            pg_cluster_info["Host"] = cluster_name + "-ha." + self.ns + ".svc"
            pg_cluster_info["SSLMode"] = "prefer"
            pg_cluster_info["MaintenanceDB"] = "postgres"

            pgadmin_server[str(count)] = pg_cluster_info

        pgadmin_cluster_info["Servers"] = pgadmin_server
        pg_cluster_json = json.dumps(pgadmin_cluster_info, indent=4)
        with open("pg_cluster.json", "w") as outfile:
            outfile.write(pg_cluster_json)

    def get_postgres_cluster_names(self):
        primary_label = 'postgres-operator.crunchydata.com/role=master'
        cluster_label = 'postgres-operator.crunchydata.com/cluster'
        labels = primary_label
        primary_pods = self.kube.list_namespaced_pod(namespace=self.ns,
                                                     label_selector=labels)
        for pod in primary_pods.items:
            self.cluster_names.append(pod.metadata.labels[cluster_label])

    def connect_to_kubernetes_cluster(self):
        config.load_kube_config("/Users/robertpacheco/.kube/config")
        self.kube = client.CoreV1Api()


# entry point
if __name__ == '__main__':
    rm = RegistrationManager()
    rm.register_postgres_clusters()
    # while True:
    #     time.sleep(1)
