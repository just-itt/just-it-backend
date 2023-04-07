from ninja import NinjaAPI
from accounts.api import router as auth_router

api_v1 = NinjaAPI(title="just-it Backend", version="1.0")

api_v1.add_router("/accounts/", auth_router, tags=["Account"])
