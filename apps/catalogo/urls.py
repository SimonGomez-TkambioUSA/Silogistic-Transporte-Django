from apps.catalogo.views import *
from django.urls import path

from apps.catalogo.views import EstadosListApiView
from apps.catalogo.functions import createPDFOrder, createReporteContabilidad, DownloadExcellOrdenes

app_name = 'catalogo'

urlpatterns = [

    #################### Urls para APi´s ####################

    path('estados/lista/', EstadosListApiView.as_view(), name='estados-list'),
    path('cuidad/lista/', CuidadesListApiView.as_view(), name='ciudades-list'),

    #################### Urls para procesos de clientes ####################

    path('clientes/', ClienteListTemplateView.as_view(), name='clientes-list'),
    path('clientes/nuevo/', ClienteNewApiView.as_view(), name='cliente-new'),
    path('clientes/activacion/desactivacion/', ClienteActivateDeactivateApiView.as_view(),
         name='cliente-deactivate-activate'),
    path('clientes/contactos/', ClienteContactoSaveEditApiView.as_view(), name='cliente-contacto-save-edit'),
    path('clientes/contactos/lista/', ClienteContactoListaApiView.as_view(), name='cliente-contacto-lista'),
    path('clientes/contactos/eliminar/', ClienteContactoEliminarApiView.as_view(), name='cliente-contacto-eliminar'),

    #################### Urls para procesos de proveedores ####################

    path('proveedores/', ProveedoresListTemplateView.as_view(), name='proveedores-list'),
    path('proveedor/nuevo/', ProveedoresNewApiView.as_view(), name='proveedor-new'),
    path('proveedor/nuevo/cargamasiva/', ProveedoresNewCargaMasiva.as_view(), name='proveedor-new-cargamasiva'),
    path('proveedor/editar/', ProveedoresEditApiView.as_view(), name='proveedor-edit'),
    path('proveedor/activar/desactivar/', ProveedorActivateDeactivateApiView.as_view(),
         name='proveedor-deactivate-activate'),

    #################### Urls para procesos de productos ####################

    path('productos/', ProductosListTemplateView.as_view(), name='productos-list'),
    path('producto/nuevo/', ProductoNewApiView.as_view(), name='producto-new'),
    path('producto/nuevo/cargamasiva/', ProductoNewCargaMasiva.as_view(), name='producto-new-cargamasiva'),
    path('producto/editar/', ProductoEditApiView.as_view(), name='producto-edit'),
    path('producto/activar/desactivar/', ProductoActivateDeactivateApiView.as_view(),
         name='producto-deactivate-activate'),

    #################### Urls para procesos de shipper ####################

    path('shipper/', ShipperListTemplateView.as_view(), name='shipper-list'),
    path('shipper/nuevo/', ShipperCreateApiView.as_view(), name='shipper-new'),
    path('shipper/editar/', ShipperEditApiView.as_view(), name='shipper-edit'),
    path('shipper/delivery/activar/desactivar/', ShipperDeliveryActivateDeactivateApiView.as_view(),
         name='shipper-delivery-deactivate-activate'),

    #################### Urls para procesos de delivery ####################
    path('delivery/', DeliveryListTemplateView.as_view(), name='delivery-list'),
    path('delivery/nuevo/', DeliveryCreateApiView.as_view(), name='delivery-new'),
    path('delivery/editar/', DeliveryEditApiView.as_view(), name='delivery-edit'),

    #

    #################### Urls para procesos de ordenes ####################
    path('ordenes/', OrdenesTemplateView.as_view(), name='ordenes-list'),
    path('ordenes/cliente/', OrdenesClienteTemplateView.as_view(), name='ordenes-list-customer'),
    path('ordenes/contabilidad/', OrdenContableTemplateView.as_view(), name='ordenes-list-contable'),
    
    path('orden/nueva/', OrdenCrearTemplateView.as_view(), name='orden-new'),
    path('orden/eliminar/', OrdenDeleteApiView.as_view(), name='orden-delete'),
    path('orden/historial/search/', OrdenDeleteApiView.as_view(), name='orden-search'),
    path('orden/editar/<int:orden>/', OrdenEditTemplateView.as_view(), name="orden-edit"),
    path('orden/tracking/log/', OrdenTrackingLogApiView.as_view(), name="orden-tracking-log"),

    #################### Urls para procesos de usuarios ####################
    path('usuarios/', UsuariosListTemplateView.as_view(), name='usuarios-list'),
    path('usuario/nuevo/', NewUsuarioApiView.as_view(), name='usuario-new'),
    path('usuario/eliminar/', DeleteUsuarioApiVieW.as_view(), name='usuario-delete'),
    
    
    
    #################### Urls para crear el PDF de las ordenes ####################
    path('orden/creacion/pdf/',createPDFOrder,name='orden-creacion-pdf'),


    #################### Urls para los reportes ####################
    path('reportes/contabilidad/', ReporteContabilidad.as_view() ,name="reporte-contabilidad"),
    path('reportes/rutas/', ReporteRutas.as_view(), name="reporte-rutas"),
    path('reportes/contabilidad/exportacion/', createReporteContabilidad , name="reporte-contabilidad-exportacion" ),
    path('reportes/contabilidad/exportar/', DownloadExcellOrdenes, name='reporte-contabilidad-exportar'),
    path('reportes/filtro/fechas', ReporteFiltroFechas.as_view(), name="filterDate-reportes"),
    path('reportes/filtro/direccion', ReporteFiltroCiudades.as_view(), name="filterAddress-reportes"),

    #################### Urls para los flujos de creación de reportes para los clientes  ####################
    path('reportes/clientes/listado/', ReporteClienteListado.as_view(), name="reporte-cliente-listado"),
    path('reportes/clientes/add/', ReporteClienteAdd.as_view(), name="reporte-cliente-add"),
    path('reportes/clientes/delete/', ReporteClienteDelete.as_view(), name="reporte-cliente-delete"),
    path('reportes/clientes/listado/sidebar/', ReportesGeneradosCliente.as_view(),name="reporte-cliente-sidebar"),
    
    #################### Urls para los flujos de Utilidad ###################
    path('utilidad/', UtilidadOrdenes.as_view(), name='utilidad-ordenes'),
    
    
    
    
    #################### Urls para los flujos de la paginacion ###################
    path('listado/ordenes/paginacion/', listadoOrdenesPaginacion.as_view(), name='listado-ordenes-paginacion'),
    
    #################### Urls para los flujos del calendario semanal de ordenes ###################
    
    path('calendario/semanal/', CalendarioSemanalOrdenes.as_view(),name='ordenes-calendario-semanal'),
    
    
    

    
    

]
