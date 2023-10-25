from django.conf import settings
from django.http import JsonResponse
from django.core.mail import send_mail
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from .forms import SignupForm


@api_view(["GET"])
def me(request):
    return JsonResponse(
        {
            "id": request.user.id,
            "name": request.user.name,
            "email": request.user.email,
            "avatar": request.user.get_avatar(),
        }
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def signup(request):
    data = request.data
    message = "success"

    form = SignupForm(
        {
            "email": data.get("email"),
            "name": data.get("name"),
            "password1": data.get("password1"),
            "password2": data.get("password2"),
        }
    )

    if form.is_valid():
        user = form.save()
        user.is_active = True
        user.save()

        # url = f"{settings.WEBSITE_URL}/activateemail/?email={user.email}&id={user.id}"

        # send_mail(
        #     "Please verify your email",
        #     f"The url for activating your account is: {url}",
        #     "noreply@wey.com",
        #     [user.email],
        #     fail_silently=False,
        # )
    else:
        message = form.errors.as_json()

    print(message)

    return JsonResponse({"message": message}, safe=False)
