from django.conf.urls import url
from accounts import views

urlpatterns = [
    url(r'^edit/(?P<pk>\d+)$', views.AccountEditView.as_view(),
        name="account-edit"),
]
