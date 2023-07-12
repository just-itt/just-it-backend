from accounts.schema import AuthBearer


def custom_auth(request):
    token = request.headers.get("Authorization")
    if token:
        token = token.split("Bearer")[1].strip()
        return AuthBearer().authenticate(request=request, token=token)
    return 401
