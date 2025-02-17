
# 定义自定义异常类
class NonSuccessStatusCodeError(Exception):
    def __init__(self, status_code, message="Non-success status code received"):
        self.status_code = status_code
        self.message = f'{status_code} {message}'
        super().__init__(self.message)
