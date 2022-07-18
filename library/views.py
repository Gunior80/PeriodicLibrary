import base64

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView

# Create your views here.
from library import models


class ViewerPDF(ListView):
    model = models.Periodical
    context_object_name = 'periodical'
    template_name = 'library/viewer.html'


class LoadPDF(View):
    http_method_names = ['post']

    def post(self, request, **kwargs):
        response = {"url": None}
        id = request.POST.get('document')
        if id:
            object = models.Instance.objects.get(id=id)
            response["url"] = object.file.url
        return HttpResponse(JsonResponse(response), content_type="application/json")
