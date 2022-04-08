from baseuser.views import index,VerifyEmail, Login, Logout, Register,CSRFToken, RSAPubKey, http_404_handler,CASLogin
from django.urls import path,re_path
handler404 = http_404_handler
urlpatterns = [
    path('index/',index, name='index'),
    # path('api/', include(router.urls) ),
    path('api/login/', Login.as_view()),
    # path('test/', Test.as_view()),
    # path('testpage/', TestPage.as_view()),
    path('api/logout/', Logout.as_view()),
    path('api/register/', Register.as_view()),
    path('api/common/CSRFToken/', CSRFToken.as_view()),
    path('api/common/rsa_pk/', RSAPubKey.as_view()),
    path('api/verify/', VerifyEmail.as_view()),
    re_path(r'^cas/login/?$', CASLogin.as_view())
    # path('api/token/refresh/', TokenRefreshView.as_view())
]

