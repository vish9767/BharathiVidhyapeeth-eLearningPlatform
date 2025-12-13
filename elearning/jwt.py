from rest_framework_simplejwt.tokens import RefreshToken

def generate_jwt(user):
    refresh = RefreshToken.for_user(user)  # works even if user is custom model
    access = refresh.access_token          # <-- here

    # Add custom claims
    refresh['user_id'] = user.u_id
    refresh['email'] = user.email
    refresh['level'] = user.level  # will store enum value (1 or 2)

    return {
        "refresh": str(refresh),
        "access": str(access)
    }


from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from .models import User

class MyJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Returns a user based on user_id claim in token instead of Django auth user.
        """
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise InvalidToken("Token contained no user_id")

        try:
            user = User.objects.get(u_id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        return user
