from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.http.response import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404
from django.views import generic
from django.utils.translation import ugettext as _
from django.utils import timezone
from travels.models import Travel
from travels.forms import TravelForm
from travels.tasks import travel_submit_task


class TravelList(generic.ListView):
    """
    List view of all requests created by the given user. This view is shown
    on the website in "My Requests" page.
    """
    model = Travel

    def get_queryset(self):
        return Travel.objects.filter(traveller_id=self.request.user.id)


class TravelDetail(generic.DetailView):
    """
    Detail view for a single request created by the given user. This view is
    shown on the website when user clicks on a single request in "My Requests"
    page.
    """
    model = Travel

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user != self.object.traveller:
            return HttpResponseForbidden()
        return super(TravelDetail, self).get(request, *args, **kwargs)


class TravelCreate(generic.CreateView):
    """
    Create view for request creation page. Upon clicking "Create a request"
    user will be able to create a new request and that page is generated
    by this view.
    """
    model = Travel
    form_class = TravelForm

    def get(self, request, *args, **kwargs):
        if request.user.is_driver:
            return HttpResponseRedirect(reverse('home-page'))
        return super(TravelCreate, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Change the traveller to the user
        """
        form.instance.traveller = self.request.user
        self.object = form.save()
        messages.success(self.request, _('Request successfully created'))
        travel_submit_task.delay(self.object.id)
        return HttpResponseRedirect(self.get_success_url())


class TravelUpdate(generic.UpdateView):
    """
    Update view for request edit page. Upon clicking "Edit" button on the
    request view page, user will be able to update a request by utilising
    this view.
    """
    model = Travel
    form_class = TravelForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user != self.object.traveller:
            return HttpResponseForbidden()
        return super(TravelUpdate, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save()
        messages.success(self.request, _('Request successfully updated'))
        travel_submit_task.delay(self.object.id)
        return HttpResponseRedirect(self.get_success_url())


class TravelDelete(generic.DeleteView):
    """
    User wishing to delete a request will be handled by this view. Note that
    deletion function is handled by single JavaScript popup question where
    user can choose whether delete the request or keep it.
    """
    model = Travel

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user != self.object.traveller:
            return HttpResponseForbidden()
        return super(TravelDelete, self).get(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, _('Request successfully deleted'))
        return reverse_lazy('travels')


class DriverTravelAssign(generic.View):
    """
    POST only view which assigns a given travel to a driver
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        if request.user.is_driver != True:
            return HttpResponseRedirect(reverse('travels'))
        self.object = get_object_or_404(Travel, pk=kwargs['pk'])
        if not self.object.assigned_vehicle:
            return HttpResponseForbidden()
        if request.user not in self.object.assigned_vehicle.drivers.all():
            return HttpResponseForbidden()
        # Seems like the call is genuine - continue
        self.object.assigned_driver = request.user
        self.object.save()
        return HttpResponseRedirect(reverse('driver-detail',
            args=[self.object.id]))


class DriverTravelRelease(generic.View):
    """
    POST only view which releases a given travel by a driver
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        if request.user.is_driver != True:
            return HttpResponseRedirect(reverse('travels'))
        self.object = get_object_or_404(Travel, pk=kwargs['pk'])
        if not self.object.assigned_vehicle:
            return HttpResponseForbidden()
        if request.user != self.object.assigned_driver:
            return HttpResponseForbidden()
        # Seems like the call is genuine - continue
        self.object.assigned_driver = None
        self.object.save()
        return HttpResponseRedirect(reverse('vehicle-list'))


class DriverTravelList(generic.ListView):
    """
    List view of all request tasks assigned to the given driver. Drivers
    can list these requests by clicking on "My Tasks" link in the navbar.
    """
    template_name = 'travels/driver_travel_list.html'

    def get(self, request, *args, **kwargs):

        if request.user.is_driver != True:
            return HttpResponseRedirect(reverse('travels'))

        return super(DriverTravelList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        # Get the travels for the user
        return Travel.objects.filter(assigned_driver=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Add additional data to context
        """
        context = super(DriverTravelList, self).get_context_data(**kwargs)
        context.update({
            "current_time": timezone.now(),
        })
        return context


class VehicleTravelList(DriverTravelList):
    """
    List view of all request tasks assigned to a vehicle but not to a driver.
    Drivers can list these items by clicking on "Open Assignments" link
    in the navbar. This is a subclass of DriverTravelList.
    """
    template_name = 'travels/vehicle_travel_list.html'

    def get_queryset(self):
        # Get the travels for the user
        return Travel.objects.filter(
            assigned_vehicle__drivers__in=(self.request.user,),
            assigned_driver=None,
        )


class DriverTravelDetail(generic.DetailView):
    """
    Detail view of a request assigned to the driver. This view is
    shown on the website when a driver user clicks on a single request in
    "My Requests" page.
    """
    template_name = 'travels/driver_travel_detail.html'
    model = Travel

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.is_driver != True:
            # In case if the requester is the owner  of the travel redirect
            if request.user == self.object.traveller:
                return HttpResponseRedirect(reverse('travel-detail',
                    args=[self.object.id]))
            return HttpResponseForbidden()
        if not self.object.assigned_vehicle:
            return HttpResponseForbidden()
        if request.user != self.object.assigned_driver:
            return HttpResponseForbidden()
        if request.user not in self.object.assigned_vehicle.drivers.all():
            return HttpResponseForbidden()
        return super(DriverTravelDetail, self).get(request, *args, **kwargs)


class PreviewTravelDetail(DriverTravelDetail):
    """
    Preview detail view for the drivers to get a general idea about the travel.
    Drivers will need to assign it to themselves before working on it.
    """
    template_name = 'travels/preview_travel_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.is_driver != True:
            # In case if the requester is the owner  of the travel redirect
            if request.user == self.object.traveller:
                return HttpResponseRedirect(reverse('travel-detail',
                    args=[self.object.id]))
            return HttpResponseForbidden()
        if not self.object.assigned_vehicle:
            return HttpResponseForbidden()
        if self.object.assigned_driver:
            return HttpResponseForbidden()
        if request.user not in self.object.assigned_vehicle.drivers.all():
            return HttpResponseForbidden()
        return super(DriverTravelDetail, self).get(request, *args, **kwargs)
