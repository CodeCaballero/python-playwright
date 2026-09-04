from config.settings import API_BASE_URL


class ApiClient:
    def __init__(self, request, base_url: str | None = None):
        if base_url is None:
            base_url = API_BASE_URL
        self.request = request
        self.base_url = base_url.rstrip("/")

    def post_login(self, username: str, password: str, remember: bool = False):
        data: dict[str, str | bool] = {"username": username, "password": password}
        if remember:
            data["remember"] = True
        return self.request.post(f"{self.base_url}/login", data=data)

    def get_transactions(self, params: dict | None = None):
        return self.request.get(f"{self.base_url}/transactions", params=params)

    def get_transactions_contacts(self):
        return self.request.get(f"{self.base_url}/transactions/contacts")

    def get_transactions_public(self):
        return self.request.get(f"{self.base_url}/transactions/public")

    def get_transactions_export(self, params: dict | None = None):
        return self.request.get(f"{self.base_url}/transactions/export", params=params)

    def post_transaction(self, payload: dict):
        return self.request.post(f"{self.base_url}/transactions", data=payload)

    def get_transaction(self, transaction_id: str):
        return self.request.get(f"{self.base_url}/transactions/{transaction_id}")

    def patch_transaction(self, transaction_id: str, payload: dict):
        return self.request.patch(f"{self.base_url}/transactions/{transaction_id}", data=payload)

    def post_logout(self):
        return self.request.post(f"{self.base_url}/logout")

    def get_check_auth(self):
        return self.request.get(f"{self.base_url}/checkAuth")

    def get_bank_transfers(self):
        return self.request.get(f"{self.base_url}/bankTransfers")

    def get_test_data(self, entity: str):
        return self.request.get(f"{self.base_url}/testData/{entity}")

    def graphql_list_bank_accounts(self):
        query = "query { listBankAccount { id bankName accountNumber routingNumber isDeleted } }"
        return self.request.post(f"{self.base_url}/graphql", data={"query": query})

    def graphql_create_bank_account(
        self, bank_name: str, account_number: str, routing_number: str
    ):
        query = (
            "mutation($bankName: String!, $accountNumber: String!, $routingNumber: String!) { "
            "createBankAccount(bankName: $bankName, accountNumber: $accountNumber, "
            "routingNumber: $routingNumber) { id bankName accountNumber routingNumber "
            "isDeleted } }"
        )
        variables = {
            "bankName": bank_name,
            "accountNumber": account_number,
            "routingNumber": routing_number,
        }
        return self.request.post(
            f"{self.base_url}/graphql", data={"query": query, "variables": variables}
        )

    def graphql_delete_bank_account(self, bank_account_id: str):
        query = "mutation($id: ID!) { deleteBankAccount(id: $id) }"
        return self.request.post(
            f"{self.base_url}/graphql",
            data={"query": query, "variables": {"id": bank_account_id}},
        )

    def get_bank_accounts(self):
        return self.request.get(f"{self.base_url}/bankAccounts")

    def get_bank_account(self, bank_account_id: str):
        return self.request.get(f"{self.base_url}/bankAccounts/{bank_account_id}")

    def post_bank_account(self, payload: dict):
        return self.request.post(f"{self.base_url}/bankAccounts", data=payload)

    def delete_bank_account(self, bank_account_id: str):
        return self.request.delete(f"{self.base_url}/bankAccounts/{bank_account_id}")

    def get_notifications(self):
        return self.request.get(f"{self.base_url}/notifications")

    def post_notifications_bulk(self, items: list):
        return self.request.post(f"{self.base_url}/notifications/bulk", data={"items": items})

    def patch_notification(self, notification_id: str, payload: dict):
        return self.request.patch(f"{self.base_url}/notifications/{notification_id}", data=payload)

    def get_contacts(self, username: str):
        return self.request.get(f"{self.base_url}/contacts/{username}")

    def post_contact(self, contact_user_id: str):
        return self.request.post(
            f"{self.base_url}/contacts", data={"contactUserId": contact_user_id}
        )

    def delete_contact(self, contact_id: str):
        return self.request.delete(f"{self.base_url}/contacts/{contact_id}")

    def get_comments(self, transaction_id: str):
        return self.request.get(f"{self.base_url}/comments/{transaction_id}")

    def post_comment(self, transaction_id: str, content: str | None = None):
        data = {"content": content} if content is not None else {}
        return self.request.post(f"{self.base_url}/comments/{transaction_id}", data=data)

    def get_likes(self, transaction_id: str):
        return self.request.get(f"{self.base_url}/likes/{transaction_id}")

    def post_like(self, transaction_id: str):
        return self.request.post(f"{self.base_url}/likes/{transaction_id}")

    def get_users(self):
        return self.request.get(f"{self.base_url}/users")

    def get_users_search(self, q: str | None = None):
        params = {"q": q} if q is not None else None
        return self.request.get(f"{self.base_url}/users/search", params=params)

    def get_user(self, user_id: str):
        return self.request.get(f"{self.base_url}/users/{user_id}")

    def get_user_profile(self, username: str):
        return self.request.get(f"{self.base_url}/users/profile/{username}")

    def patch_user(self, user_id: str, payload: dict):
        return self.request.patch(f"{self.base_url}/users/{user_id}", data=payload)
