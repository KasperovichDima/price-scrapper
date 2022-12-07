"""Common test utils."""

def send_post_request_data(url: str, payload: RequestInScheme,
                     access_token) -> Response:
    """Request to '/report/add_products' endpoint with fake payload."""
    return client.post(url, data=payload.json(), headers=access_token))
    