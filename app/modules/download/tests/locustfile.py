from locust import HttpUser, task, between


class DownloadUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.index()

    @task(1)
    def index(self):
        self.client.get("/download")

    @task(2)
    def download_all(self):
        self.client.get("/download/all")

    @task(3)
    def download_datasets_by_date(self):
        start_date = "2000-01-01"
        end_date = "2031-01-01"

        self.client.post("/download/by-date", data={"start_date": start_date, "end_date": end_date})

    @task(4)
    def download_datasets_by_email(self):
        email = "user1@example.com"
        self.client.post("/download/by-email", data={"email": email})
