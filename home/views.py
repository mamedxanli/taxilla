from django.conf import settings
from django.contrib.auth import views
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views import generic

class HomeView(generic.TemplateView):
    """
    View to render the home page
    """
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        """
        Add additional data to context
        """
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update({
            "current_time": timezone.now(),
            "site_name": settings.GRAPPELLI_ADMIN_TITLE,
        })
        return context

    def get_guidelines(self):
        """
        Function generates a data structure to have on a home page
        depending on user type in the following format:
        [
            {
                'name': 'Request a car',
                'description': 'This is to request a car',
                'icon': 'car'
            },
            {
                'name': 'My profile'',
                'description': 'This is to see your profile',
                'icon': 'profile'
            },
            ...
        ]
        """
        user = self.request.user
        guidelines = []
        if not user.is_driver:
            guidelines.append({
                'name': 'Request a Car',
                'description': (
                    'Use the request a car link to create a new car transfer '
                    'request which will let you to choose a pickup and destin'
                    'ation points. You will be able to input an exact address'
                    ' or use an embedded Google Maps to pin point the locatio'
                    'ns'),
                'icon': 'icon-pointer',
            })
            guidelines.append({
                'name': 'My Requests',
                'description': (
                    'Here you can find all your current and previous requests'
                    ' and also check their statuses. You will also be able to'
                    ' see which car and driver was assigned to the particular'
                    ' transfer request.'),
                'icon': 'icon-list'
            })
        else:
            guidelines.append({
                'name': 'Requests',
                'description': (
                    'Here you could see the list of transfer requests assigne'
                    'd to you as a driver. You will be able to see the pickup'
                    ' and drop-off locations for each transfer request. You w'
                    'ill also be able to see the details about the number of '
                    'passengers and a contact phone to communicate.'),
                'icon': 'icon-directions',
            })
        guidelines.append({
            'name': 'Help',
            'description': (
                'For more detailed information about the system usage, exampl'
                'es and overall documentation, head to Help section by clicki'
                'ng on the link in the navigational bar on the top. Of course'
                ' you can always call the call centre for more information.'),
            'icon': 'icon-question',
        })
        guidelines.append({
            'name': 'My Profile',
            'description': (
                'Here you can view and update your personal information such '
                'as a telephone number, which is important to keep up to dat '
                'e so the drivers could keep in touch with when they arrive o'
                'r in case they need to give you an important update about up'
                'coming trip'),
            'icon': 'icon-user',
        })
        guidelines.append({
            'name': 'Sign Out',
            'description': (
                'For your security, it is always a good idea to sign out from'
                ' the system when using a public computer. When you are using'
                ' your personal one - it is handy to stay signed in for quick'
                'er interaction with the system.'),
            'icon': 'icon-logout',
        })
        return guidelines

# Below function is being deprecated
def custom_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/home/")
        # return reverse('home-page')
    else:
        return views.login(request, template_name='login.html')
