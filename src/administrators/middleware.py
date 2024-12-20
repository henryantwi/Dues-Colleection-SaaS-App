from .models import CustomUser

class CustomUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.user.__class__ = CustomUser
        return self.get_response(request)
