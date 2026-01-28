class APIError(Exception):
    def __init__(self, status_code: str, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"[{self.status_code}] {self.message}"
