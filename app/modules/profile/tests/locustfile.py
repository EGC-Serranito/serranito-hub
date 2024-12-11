from locust import HttpUser, task, between
from faker import Faker
import random

fake = Faker()


class ProfileUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.login()

    def login(self):
        response = self.client.post(
            "/login",
            data={
                "email": "test@example.com",
                "password": "test1234"
            }
        )
        if response.status_code != 200:
            print("Login failed!")
        else:
            print("Login successful!")

    @task(3)
    def edit_profile(self):
        """
        Simulates edit data functionality.
        """
        profile_data = {
            "username": fake.user_name(),
            "email": fake.email(),
            "bio": fake.sentence(),
        }
        response = self.client.post(
            "/profile/edit",
            data=profile_data
        )
        if response.status_code == 200:
            print("Profile edited successfully")
        else:
            print(f"Edit profile failed: {response.status_code}")

    @task(2)
    def view_profile_summary(self):
        """
        Simulates access to profile page.
        """
        self.client.get("/profile/summary")

    @task(1)
    def view_another_user_profile(self):
        """
        Simulates access to another user page.
        """

        user_id = random.randint(1, 2)
        self.client.get(f"/profile/view_profile/{user_id}")

    def on_stop(self):
        self.logout()

    def logout(self):
        self.client.get("/logout")
