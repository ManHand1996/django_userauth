from baseuser.views import index,VerifyEmail, Login, Logout, Register,CSRFToken, RSAPubKey, http_404_handler,CASLogin
from django.urls import path,re_path
handler404 = http_404_handler
urlpatterns = [
    path('index/',index, name='index'),
    # path('api/', include(router.urls) ),
    # path('api/login/', Login.as_view()),
    # path('test/', Test.as_view()),
    # path('testpage/', TestPage.as_view()),
    # path('api/logout/', Logout.as_view()),
    path('cas/register/', Register.as_view()),
    path('cas/common/CSRFToken/', CSRFToken.as_view()),
    path('cas/common/rsa_pk/', RSAPubKey.as_view()),
    path('cas/verify/', VerifyEmail.as_view()),
    re_path(r'^cas/login/?$', CASLogin.as_view(),  name='cas_login')  # 重写cas_login
    # path('api/token/refresh/', TokenRefreshView.as_view())
]

