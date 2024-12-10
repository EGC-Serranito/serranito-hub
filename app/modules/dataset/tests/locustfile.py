from locust import HttpUser, TaskSet, task
# from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token


class DatasetBehavior(TaskSet):
    def on_start(self):
        self.dataset()

    @task(2)
    def dataset(self):
        response = self.client.get("/dataset/upload")
        get_csrf_token(response)

    @task(1)
    def dataset_rate(self):
        for i in range(4):
            dataset_id = i + 1
            self.client.post(f"/rate_dataset/{dataset_id}", data={"rate": (i*2) % 5})


class UploadEditFileBehavior(TaskSet):
    def on_start(self):
        self.upload_edit_file()

    @task
    def upload_edit_file(self):
        self.client.post("/dataset/1/upload/files", data={
            "file_id": 1,
            "content": "contenido "
        })


class UpdateDatasetBehavior(TaskSet):
    def on_start(self):
        self.update_dataset()

    @task
    def update_dataset(self):
        self.client.get("/dataset/update/1")


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior, UploadEditFileBehavior, UpdateDatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
