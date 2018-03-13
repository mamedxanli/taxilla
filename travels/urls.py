from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from travels import views

urlpatterns = [
    url(r'^$', login_required(views.TravelList.as_view()), name='travels'),
    url(r'^(?P<pk>\d+)/$',
        login_required(views.TravelDetail.as_view()), name='travel-detail'),
    url(r'^delete/(?P<pk>\d+)/$',
        login_required(views.TravelDelete.as_view()), name='travel-delete'),
    url(r'^driver_assign/(?P<pk>\d+)/$',
        login_required(views.DriverTravelAssign.as_view()),
        name='driver-assign'),
    url(r'^driver_release/(?P<pk>\d+)/$',
        login_required(views.DriverTravelRelease.as_view()),
        name='driver-release'),
    url(r'^driver_list/$',
        login_required(views.DriverTravelList.as_view()), name='driver-list'),
    url(r'^driver_detail/(?P<pk>\d+)/$',
        login_required(views.DriverTravelDetail.as_view()),
        name='driver-detail'),
    url(r'^edit/(?P<pk>\d+)/$',
        login_required(views.TravelUpdate.as_view()), name='travel-edit'),
    url(r'^new$', login_required(views.TravelCreate.as_view()),
        name='travel-new'),
    url(r'^preview/(?P<pk>\d+)/$',
        login_required(views.PreviewTravelDetail.as_view()),
        name='preview-detail'),
    url(r'^vehicle_list/$',
        login_required(views.VehicleTravelList.as_view()), name='vehicle-list'),
]
