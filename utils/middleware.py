import hmac, hashlib, json
from django.http import JsonResponse
from transfers.models import User

class RequestSignatureMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ["POST", "PUT"]:
            try:
                body = request.body.decode()
                sign_header = request.headers.get("request-sign")
                user_id = request.user.id  # предполагаем, что юзер аутентифицирован
                secret = User.objects.get(id=user_id).secret

                expected_sign = hmac.new(
                    secret.encode(),
                    body.encode(),
                    hashlib.sha256
                ).hexdigest()

                if expected_sign != sign_header:
                    return JsonResponse({"error": "Invalid signature"}, status=403)
            except Exception:
                return JsonResponse({"error": "Signature check failed"}, status=400)
        return self.get_response(request)
