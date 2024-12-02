from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing
import random


class DatasetBehavior(TaskSet):
    def on_start(self):
        self.dataset()

    @task(2)
    def dataset(self):
        response = self.client.get("/dataset/upload")
        get_csrf_token(response)

    @task(1)
    def dataset_rate(self):
        dataset_id = random.choice([1, 2, 3, 4])
        self.client.post(f"/rate_dataset/{dataset_id}", data={"rate": 5})


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
