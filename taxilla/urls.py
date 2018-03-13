from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.views.static import serve
from home.views import custom_login

urlpatterns = [
    url(r'^', include('home.urls')),
    url(r'^', include('pages.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^docs/html/(?P<path>.*)', staff_member_required(serve,
        login_url='home-page'), {'document_root': 'docs/html'}, name='docs'),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^requests/', include('travels.urls')),
    url(r'^vehicles/', include('vehicles.urls')),
]
