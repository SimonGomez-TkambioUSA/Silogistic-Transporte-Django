import json

from django.shortcuts import render
from django.views.generic import TemplateView

from apps.catalogo.models import PersonaSistema, FormatoCliente, Orden


# Create your views here.



class DashboardReportesCliente(TemplateView):
    template_name = 'cliente/dashboard_reporte.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardReportesCliente, self).get_context_data(**kwargs)
        cadenaIdentificador = self.request.GET.get('idReporte')
        cadenaIdentificador = cadenaIdentificador[5:len(cadenaIdentificador)]
        idReporte = cadenaIdentificador[0:-5]
        objReporte = FormatoCliente.objects.get(pk=idReporte)
        context['reporte'] = objReporte

        # # Obtenemos el id del usuario que esta iniciando sesión para obtener el cliente que pertecene y asi buscar las ordenes y el reporte
        idUser = self.request.user.pk
        objPersona = PersonaSistema.objects.get(usuario_id=idUser)
        context['arrOrdenes'] = Orden.objects.filter(cliente_id=objPersona.cliente.pk).order_by('-pk')
        return context