import requests


class DatabaseApi:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def create_user(self, user: dict):
        response = requests.post(f"{self.base_url}/users", json=user)
        response.raise_for_status()
        return response

    def reset_db(self):
        response = requests.post(f"{self.base_url}/testData/seed")
        response.raise_for_status()
        return response
