import time
from functools import wraps

# TODO: Viết hàm decorator retry_on_failure tại đây
def retry_on_failure(retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Viết logic retry ở đây
            pass

        return wrapper

    return decorator


# --- MÔ PHỎNG SỬ DỤNG TRONG TEST CASE ---
attempt_counter = 0


@retry_on_failure(retries=3, delay=1)
def call_flaky_api():
    global attempt_counter
    attempt_counter += 1
    print(f"--> Đang gọi API (Lần {attempt_counter})...")

    # Giả lập 2 lần đầu bị timeout, lần 3 mới thành công
    if attempt_counter < 3:
        raise ConnectionError("504 Gateway Timeout")

    return {"status_code": 200, "message": "Success"}


if __name__ == "__main__":
    result = call_flaky_api()
    print("KẾT QUẢ:", result)