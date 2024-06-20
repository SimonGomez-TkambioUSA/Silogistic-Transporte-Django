from apps.catalogo.views import *
from django.urls import path

from apps.catalogo.views import EstadosListApiView
from apps.catalogo.functions import createPDFOrder, createReporteContabilidad
from apps.customer.functions import createReportCustomerDinamic
from apps.customer.views import DashboardReportesCliente

app_name = 'customer'

urlpatterns = [
    path('reportes/', DashboardReportesCliente.as_view(), name="reportes-cliente-dashboard"),
    path('reportes/exportar/', createReportCustomerDinamic, name="reportes-cliente-dashboard-export")

]
