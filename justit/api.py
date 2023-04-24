from ninja import NinjaAPI
from accounts.api import router as auth_router
from members.api import router as member_router
from posts.api import router as post_router
from tags.api import router as tag_router

api_v1 = NinjaAPI(title="Just-it Backend", version="1.0")

api_v1.add_router("/accounts", auth_router, tags=["Account"])
api_v1.add_router("/members", member_router, tags=["Member"])
api_v1.add_router("/posts", post_router, tags=["Post"])
api_v1.add_router("/tags", tag_router, tags=["Tag"])
