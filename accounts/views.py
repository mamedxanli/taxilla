from accounts.forms import TaxillaUserForm
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views import generic


class AccountEditView(generic.UpdateView):
    """
    This view shows profile page where user can update their data
    """
    model = get_user_model()
    form_class = TaxillaUserForm
    template_name = "accounts/account_edit.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.username != self.object.username:
            return HttpResponseRedirect(reverse('account-edit',
                args=(request.user.id,)))

        return super(AccountEditView, self).get(request, *args, **kwargs)
