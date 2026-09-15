from locust import HttpUser, task, between
import os

class WebsiteUser(HttpUser):
    # Thời gian chờ ngẫu nhiên giữa các hành động (từ 1 đến 5 giây)
    wait_time = between(1, 5)
    host = "https://google.com"
    @task(3)  # Trọng số lớn hơn (chạy thường xuyên hơn)
    def view_homepage(self):
        """Giả lập người dùng truy cập trang chủ"""
        self.client.get("/")

    @task(1)  # Trọng số nhỏ hơn
    def login_user(self):
        """Giả lập người dùng gửi dữ liệu đăng nhập"""
        payload = {"username": "test_user", "password": "secure_password"}
        headers = {"Content-Type": "application/json"}

        # Gửi request POST kèm data json
        self.client.post("/api/login", json=payload, headers=headers)
if __name__ == "__main__":
    cmd = f"locust -f {__file__} --headless -u 10 -r 2 --run-time 30s"
    os.system(cmd)