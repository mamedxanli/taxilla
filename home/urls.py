from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView
from home import views

urlpatterns = [
    url(r'^$', login_required(views.HomeView.as_view()),name="home-page"),
    url(r'^panel/', RedirectView.as_view(url=reverse_lazy('admin:index')),
        name="panel"),
] 
