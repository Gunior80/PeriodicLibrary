from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import ListView, TemplateView, DetailView
from library import models, utils
from library.models import Address
from taggit.models import Tag
from django.core.exceptions import PermissionDenied


class Index(ListView):
    model = models.Periodical
    context_object_name = 'periodicals'
    template_name = 'library/index.html'

    def get(self, request, *args, **kwargs):
        request.session['newview'] = True
        request.session['viewed'] = []
        return super().get(self, request, *args, **kwargs)


class PeriodicView(DetailView):
    # Load catalog
    model = models.Periodical
    context_object_name = 'periodical'
    template_name = 'library/catalog.html'


class LoadURL(View):
    # Load instance url
    http_method_names = ['post']

    def post(self, request, **kwargs):
        response = {"url": None}
        id = request.POST.get('document')
        if id:
            object = models.Instance.objects.get(id=id)
            response["url"] = object.file.url
            addr = utils.get_ip(request)
            request.session['material'] = object.file.url
            if Address.is_client(addr):
                client = Address.get_client(addr)
                if request.session.get('newview', False):
                    client.inc_visit(object.periodical)
                    request.session['newview'] = False
                if id not in request.session['viewed']:
                    client.inc_view(object.periodical)
                    request.session['viewed'].append(id)
        return HttpResponse(JsonResponse(response), content_type="application/json")


@method_decorator(xframe_options_exempt, name='dispatch')
class Viewer(TemplateView):
    # Load pdf viewer
    template_name = 'library/viewer.html'


class LoadMenu(View):
    # Load json structs for generate treeview
    http_method_names = ['post']

    def post(self, request, **kwargs):
        response = []
        request_periodical = request.POST.get('periodic')
        request_string = request.POST.get('search-string')
        value = request.POST.get('value')
        periodic = models.Periodical.objects.filter(id=request_periodical).first()
        if periodic:
            if request_string:
                response = periodic.json_search(request_string)
            else:
                if value:
                    if value.isdigit():
                        response = periodic.json_months(value)
                    else:
                        data = value.split('_')
                        if len(data) == 2:
                            response = periodic.json_instances(*data)
                else:
                    response = periodic.json_years()
        return HttpResponse(JsonResponse(response, safe=False), content_type="application/json")


class LoadAutocomplete(View):
    # Load tags for seach field
    http_method_names = ['post']

    def post(self, request, **kwargs):
        response = []
        request_periodical = request.POST.get('periodic')
        periodical = models.Periodical.objects.filter(id=request_periodical).first()
        if periodical:
            tags = Tag.objects.filter(instance__periodical=periodical).values_list('name', flat=True).distinct()
            response = list(tags)
        return HttpResponse(JsonResponse(response, safe=False), content_type="application/json")


def secure(request):
    # For Nginx request. This is necessary for a one-time download
    if request.session['material'] == request.META.get('HTTP_X_ORIGINAL_URI'):
        request.session['material'] = None
        return HttpResponse("")
    else:
        raise PermissionDenied()
