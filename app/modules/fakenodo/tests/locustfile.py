from locust import HttpUser, task, between


class FakenodoUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def test_connection(self):
        """Simulate GET request to test_connection_fakenodo"""
        self.client.get("/fakenodo/api")

    @task
    def create_fakenodo(self):
        """Simulate POST request to create_fakenodo"""
        self.client.post("/fakenodo/api")

    @task
    def deposition_files(self):
        """Simulate POST request to deposition_files_fakenodo"""
        depositionid = "12345"
        self.client.post(f"/fakenodo/api/{depositionid}/files")

    @task
    def delete_deposition(self):
        """Simulate DELETE request to delete_deposition_fakenodo"""
        depositionid = "12345"
        self.client.delete(f"/fakenodo/api/{depositionid}")

    @task
    def publish_deposition(self):
        """Simulate POST request to publish_deposition_fakenodo"""
        depositionid = "12345"
        self.client.post(f"/fakenodo/api/{depositionid}/actions/publish")

    @task
    def get_deposition(self):
        """Simulate GET request to get_deposition_fakenodo"""
        depositionid = "12345"
        self.client.get(f"/fakenodo/api/{depositionid}")
