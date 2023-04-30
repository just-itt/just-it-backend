from django.utils.deprecation import MiddlewareMixin


class PutPatchWithFileFormMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if (
            request.method in ("PUT", "PATCH")
            and request.content_type != "application/json"
        ):
            if hasattr(request, "_post"):  # post 데이터 삭제
                del request._post
                del request._files
            try:
                initial_method = request.method
                request.method = "POST"  # 리퀘스트 메서드를 POST로 임시 변경
                request.META["REQUEST_METHOD"] = "POST"
                request._load_post_and_files()  # 이 부분이 핵심
                request.META["REQUEST_METHOD"] = initial_method  # 원래 메서드로 되돌림
                request.method = initial_method  # 원래 메서드로 되돌림
            except Exception:
                pass
