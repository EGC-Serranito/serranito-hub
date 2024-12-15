from locust import HttpUser, TaskSet, task, between
from core.environment.host import get_host_for_locust_testing


class HubfileBehavior(TaskSet):
    def on_start(self):
        self.index()

    @task
    def index(self):
        response = self.client.get("/hubfile")

        if response.status_code != 200:
            print(f"Hubfile index failed: {response.status_code}")


class HubfileUser(HttpUser):
    tasks = [HubfileBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()

class FileUploadBehavior(TaskSet):
    @task(1)
    def upload_valid_file(self):
        files = {'file': ('valid.uvl', 'content of a valid UVL file', 'application/octet-stream')}
        response = self.client.post("/hubfile/upload", files=files)
        assert response.status_code == 200

    @task(1)
    def upload_invalid_file(self):
        files = {'file': ('invalid.txt', 'invalid content', 'application/octet-stream')}
        response = self.client.post("/hubfile/upload", files=files)
        assert response.status_code == 400

    @task(1)
    def upload_large_file(self):
        large_content = "a" * 11 * 1024 * 1024
        files = {'file': ('large.uvl', large_content, 'application/octet-stream')}
        response = self.client.post("/hubfile/upload", files=files)
        assert response.status_code == 413

class FileUploadUser(HttpUser):
    tasks = [FileUploadBehavior]
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()
