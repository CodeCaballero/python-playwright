from config.settings import WEB_BASE_URL
from playwright.sync_api import expect

from test.web.pages.base_page import BasePage


class NotificationsPage(BasePage):
    @property
    def _loc_heading(self):
        return self.page.get_by_role("heading", name="Notifications", exact=True)

    @property
    def _loc_notification_items(self):
        return self.page.locator('[data-test^="notification-list-item-"]')

    def load(self):
        self.navigate_to(f"{WEB_BASE_URL.rstrip('/')}/notifications")

    def check_notifications_list_visible(self):
        expect(self._loc_heading).to_be_visible()
        expect(self._loc_notification_items.first).to_be_visible()

    def mark_first_notification_as_read(self):
        first_item = self._loc_notification_items.first
        text = first_item.text_content()
        first_item.get_by_role("button", name="Dismiss").click()
        return text

    def check_notification_not_visible(self, text: str):
        expect(self.page.get_by_text(text)).to_have_count(0)
