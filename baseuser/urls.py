from baseuser.views import index,Test,TestPage, Login, Logout, Register,CSRFToken
from django.urls import path,include

urlpatterns = [
    path('index/',index, name='index'),
    # path('api/', include(router.urls) ),
    path('login/', Login.as_view()),
    # path('test/', Test.as_view()),
    path('testpage/', TestPage.as_view()),
    path('logout/', Logout.as_view()),
    path('register/', Register.as_view()),
    path('CSRFToken/', CSRFToken.as_view())
    # path('api/token/refresh/', TokenRefreshView.as_view())
]

