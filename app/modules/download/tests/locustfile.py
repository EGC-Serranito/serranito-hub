from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing


class DownloadBehavior(TaskSet):
    def on_start(self):
        self.index()

    @task
    def index(self):
        response = self.client.get("/download")

        if response.status_code != 200:
            print(f"Download index failed: {response.status_code}")


class DownloadUser(HttpUser):
    tasks = [DownloadBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
