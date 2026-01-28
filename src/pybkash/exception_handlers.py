from .exceptions import APIError

def raise_api_exception(response: dict):
    status_code = response.get("statusCode")
    if not status_code: # no status_code sent by api, the api does it when nothing goes wrong
        return
    if status_code == "0000":
        return
    raise APIError(status_code=response["statusCode"], message=response["statusMessage"])

