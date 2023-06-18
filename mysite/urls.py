from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from chat import routing
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


urlpatterns = [
    path("chatapi/", include("chat.urls")),
    path("admin/", admin.site.urls),
    path('ws/', include(routing.websocket_urlpatterns)),
    ]


urlpatterns += [
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
