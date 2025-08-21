from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.views import View

class IndexPageView(TemplateView):
    template_name = "main/index.html"
    
class ChangeLanguageView(TemplateView):
    template_name = "main/change_language.html"

class HomeRedirectView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # User sudah login → tampilkan IndexPageView
            return IndexPageView.as_view()(request, *args, **kwargs)
        else:
            # User belum login → redirect ke halaman login
            return redirect('accounts:log_in')