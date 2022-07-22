import base64

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import ListView, TemplateView

# Create your views here.
from library import models, utils
from library.models import Address


class Catalog(ListView):
    model = models.Periodical
    context_object_name = 'periodical'
    template_name = 'library/catalog.html'

    def get(self, request, *args, **kwargs):
        request.session['newview'] = True
        return super().get(self, request, *args, **kwargs)

class LoadURL(View):
    http_method_names = ['post']

    def post(self, request, **kwargs):
        response = {"url": None}
        id = request.POST.get('document')
        if id:
            object = models.Instance.objects.get(id=id)
            response["url"] = object.file.url
            addr = utils.get_ip(request)
            if Address.is_client(addr):
                client = Address.get_client(addr)
                if request.session.get('newview', False):
                    client.inc_visit(object.periodical) # "здесь реализовать инкрементирование посещения архива"
                    request.session['newview'] = False
                client.inc_view(object.periodical) # "здесь реализовать инкрементирование просмотренных ресурсов архива"
        return HttpResponse(JsonResponse(response), content_type="application/json")


@method_decorator(xframe_options_exempt, name='dispatch')
class Viewer(TemplateView):
    template_name = 'library/viewer.html'
