from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from pages import views

urlpatterns = [
    url(r'^help/users$', login_required(views.HelpView.as_view()),
        name="help-page"),
    url(r'^help/drivers$', login_required(views.HelpDriverView.as_view()), 
        name="help-page-driver"),
]
