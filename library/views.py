import base64

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, ListView

# Create your views here.
from library import models


class ViewerPDF(ListView):
    model = models.Periodical
    context_object_name = 'periodical'
    template_name = 'library/viewer.html'



def load_pdf(request):
    import os
    print(00000)

    with open(os.path.join(settings.MEDIA_ROOT, 'hello.pdf'), 'rb') as file:
        response = HttpResponse(base64.encodebytes(file.read()), content_type='application/pdf')
    return response