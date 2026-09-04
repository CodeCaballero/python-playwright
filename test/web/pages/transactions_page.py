import datetime

from config.settings import WEB_BASE_URL
from playwright.sync_api import expect

from test.web.pages.base_page import BasePage


class TransactionsPage(BasePage):
    @property
    def _loc_export_button(self):
        return self.page.get_by_test_id("transaction-list-export-button")

    @property
    def _loc_user_search_input(self):
        return self.page.get_by_test_id("user-list-search-input")

    @property
    def _loc_amount_input(self):
        return self.page.get_by_role("textbox", name="Amount")

    @property
    def _loc_note_input(self):
        return self.page.get_by_role("textbox", name="Add a note")

    @property
    def _loc_pay_button(self):
        return self.page.get_by_test_id("transaction-create-submit-payment")

    @property
    def _loc_request_button(self):
        return self.page.get_by_test_id("transaction-create-submit-request")

    @property
    def _loc_detail_heading(self):
        return self.page.get_by_role("heading", name="Transaction Detail")

    @property
    def _loc_like_button(self):
        return self.page.locator('[data-test^="transaction-like-button-"]')

    @property
    def _loc_like_count(self):
        return self.page.locator('[data-test^="transaction-like-count-"]')

    @property
    def _loc_comment_input(self):
        return self.page.locator('[data-test^="transaction-comment-input-"]')

    @property
    def _loc_accept_request_button(self):
        return self.page.locator('[data-test^="transaction-accept-request-"]')

    @property
    def _loc_reject_request_button(self):
        return self.page.locator('[data-test^="transaction-reject-request-"]')

    @property
    def _loc_date_filter_button(self):
        return self.page.get_by_test_id("transaction-list-filter-date-range-button")

    @property
    def _loc_amount_filter_button(self):
        return self.page.get_by_test_id("transaction-list-filter-amount-range-button")

    @property
    def _loc_amount_filter_slider(self):
        return self.page.get_by_test_id("transaction-list-filter-amount-range-slider")

    def load_personal(self):
        self.navigate_to(f"{WEB_BASE_URL.rstrip('/')}/personal")

    def load_public(self):
        self.navigate_to(f"{WEB_BASE_URL.rstrip('/')}/public")

    def load_friends(self):
        self.navigate_to(f"{WEB_BASE_URL.rstrip('/')}/contacts")

    def load_new_transaction(self):
        self.navigate_to(f"{WEB_BASE_URL.rstrip('/')}/transaction/new")

    def load_transaction(self, transaction_id: str):
        self.navigate_to(f"{WEB_BASE_URL.rstrip('/')}/transaction/{transaction_id}")

    def click_export(self):
        with self.page.expect_download() as download_info:
            self._loc_export_button.click()
        self.page.last_download = download_info.value

    def check_csv_downloaded_with_header(self, filename: str, header: str):
        download = self.page.last_download
        content = download.path().read_text()
        lines = content.splitlines()

        assert download.suggested_filename == filename, (
            f"Expected downloaded file named '{filename}', got '{download.suggested_filename}'"
        )
        assert content.strip() != "", "Downloaded CSV file is empty"
        assert len(lines) >= 1, "Downloaded CSV file has no lines"
        assert lines[0] == header, f"Expected CSV header '{header}', got '{lines[0]}'"

    def search_user(self, full_name: str):
        self._loc_user_search_input.fill(full_name)

    def search_and_select_user(self, full_name: str):
        self.search_user(full_name)
        self.page.get_by_role("listitem").filter(has_text=full_name).first.click()

    def check_single_search_result(self, full_name: str):
        expect(self.page.get_by_role("listitem")).to_have_count(1)
        expect(self.page.get_by_role("listitem").filter(has_text=full_name)).to_be_visible()

    def create_transaction(self, receiver_name: str, amount: str, note: str, submit_button):
        self.search_and_select_user(receiver_name)
        self._loc_amount_input.fill(amount)
        self._loc_note_input.fill(note)
        submit_button.click()

    def send_payment(self, receiver_name: str, amount: str, note: str):
        self.create_transaction(receiver_name, amount, note, self._loc_pay_button)

    def send_request(self, receiver_name: str, amount: str, note: str):
        self.create_transaction(receiver_name, amount, note, self._loc_request_button)

    def check_transaction_confirmation(self, text: str):
        expect(self.page.get_by_text(text)).to_be_visible()

    def check_transaction_visible(self, description: str):
        expect(self.page.get_by_text(description)).to_be_visible()

    def check_transaction_not_visible(self, description: str):
        expect(self.page.get_by_text(description)).to_have_count(0)

    def check_transaction_detail_visible(self, description: str):
        expect(self._loc_detail_heading).to_be_visible()
        expect(self.page.get_by_test_id("transaction-description")).to_have_text(description)

    def click_like(self):
        self._loc_like_button.click()

    def check_like_count(self, count: int):
        expect(self._loc_like_count).to_have_text(str(count))

    def add_comment(self, content: str):
        self._loc_comment_input.fill(content)
        self._loc_comment_input.press("Enter")

    def check_comment_visible(self, content: str):
        expect(self.page.get_by_text(content)).to_be_visible()

    def click_accept_request(self):
        self._loc_accept_request_button.click()

    def click_reject_request(self):
        self._loc_reject_request_button.click()

    def check_request_action_buttons_hidden(self):
        expect(self._loc_accept_request_button).to_have_count(0)
        expect(self._loc_reject_request_button).to_have_count(0)

    def check_feed_has_transactions(self):
        expect(self.page.locator('[data-test^="transaction-item-"]').first).to_be_visible()

    def filter_by_last_n_days(self, days: int):
        self._loc_date_filter_button.click()
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=days)
        self.page.get_by_role("button", name=self._calendar_day_label(start_date)).click()
        self.page.get_by_role("button", name=self._calendar_day_label(today)).click()

    def check_date_filter_applied(self, days: int):
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=days)
        expected = (
            f"Date: {self._filter_summary_label(start_date)} - {self._filter_summary_label(today)}"
        )
        expect(self._loc_date_filter_button).to_have_text(expected)

    @staticmethod
    def _calendar_day_label(day: datetime.date) -> str:
        return f"{day.strftime('%B')} {day.day}, {day.year}"

    @staticmethod
    def _filter_summary_label(day: datetime.date) -> str:
        return f"{day.strftime('%b')}, {day.day} {day.year}"

    def check_no_search_results(self):
        expect(self.page.get_by_role("listitem")).to_have_count(0)

    def drag_amount_max_below_default(self):
        self._loc_amount_filter_button.click()
        track_box = self._loc_amount_filter_slider.bounding_box()
        max_thumb = self.page.get_by_role("slider").nth(1)
        thumb_box = max_thumb.bounding_box()
        assert track_box is not None, "Amount filter slider is not visible"
        assert thumb_box is not None, "Amount filter max thumb is not visible"
        start_x = thumb_box["x"] + thumb_box["width"] / 2
        start_y = thumb_box["y"] + thumb_box["height"] / 2
        target_x = track_box["x"] + track_box["width"] * 0.5
        self.page.mouse.move(start_x, start_y)
        self.page.mouse.down()
        self.page.mouse.move(target_x, start_y, steps=10)
        self.page.mouse.up()

    def check_amount_filter_narrowed(self):
        expect(self._loc_amount_filter_button).not_to_have_text("Amount: $0 - $1,000")
