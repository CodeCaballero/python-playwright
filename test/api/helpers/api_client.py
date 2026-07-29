from config.settings import API_BASE_URL


class ApiClient:
    def __init__(self, request, base_url: str | None = None):
        if base_url is None:
            base_url = API_BASE_URL
        self.request = request
        self.base_url = base_url.rstrip("/")

    def post_login(self, username: str, password: str):
        return self.request.post(
            f"{self.base_url}/login",
            data={"username": username, "password": password},
        )

    def get_transactions(self):
        return self.request.get(f"{self.base_url}/transactions")

    def post_logout(self):
        return self.request.post(f"{self.base_url}/logout")