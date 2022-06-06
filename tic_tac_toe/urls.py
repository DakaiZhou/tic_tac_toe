"""tic_tac_toe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts.views import UserRegistration, GetToken
from game.views import CreateGame, JoinGame, MakeMove, ListHighScores

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/registration/', UserRegistration.as_view(), name="account-registration"),
    path('accounts/token/', GetToken.as_view(), name="get-token"),
    path('game/create/', CreateGame.as_view(), name="create-game"),
    path('game/join/<int:pk>/', JoinGame.as_view(), name="join-game"),
    path('game/make-move/', MakeMove.as_view(), name="make-move"),
    path('game/list/high-score/', ListHighScores.as_view(), name="list-high-scores")
]
