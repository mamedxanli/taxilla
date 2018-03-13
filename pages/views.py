from django.views import generic


class HelpView(generic.TemplateView):
    """
    This view renders help page shown to users
    """
    template_name = 'pages/help.html'


class HelpDriverView(generic.TemplateView):
    """
    This view renders help page shown to drivers
    """
    template_name = 'pages/help_driver.html'
