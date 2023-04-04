from ninja import NinjaAPI
from auth.api import router as auth_router

api_v1 = NinjaAPI(title="just-it Backend", version="1.0")

api_v1.add_router("/auth/", auth_router, tags=["Auth"])
