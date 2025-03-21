from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from placement import models
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from django.conf import settings
class CompanyListDatatable(BaseDatatableView):
    model = models.Company

    columns = [
        'id', 'name', 'address', 'contact_person', 'phone',
        'email','id', 'id',
    ]
    order_columns = [
        'id', 'name', 'address', 'contact_person', 'phone',
        'email', 'id', 'id',
    ]

    max_display_length = 500

    def get_initial_queryset(self):
        return models.Company.objects.filter(soft_delete=False).order_by('-id')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(email__icontains=search) | Q(
                    phone__icontains=search) | Q(address__icontains=search)
                    |Q(contact_person__icontains=search)
            )
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append([
                item.id,
                item.name,
                item.address,
                item.contact_person,
                item.phone,
                item.email,
                '/edit-company/'+str(item.pk),
                '/delete-company/'+str(item.pk),
            ])
        return data
