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
