import json
from re import I
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import StringIO
from decimal import Decimal
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from itertools import chain



from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
import csv
from django.shortcuts import render
from datetime import datetime, timedelta

from django.db import connection

# Create your views here.
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from rest_framework.views import APIView

from datetime import datetime, timedelta

from apps.catalogo.models import Cliente, Contacto_Cliente, Proveedor, Producto, Pais, Estado, Ciudad, Shipper_Delivery, \
    Orden, Orden_Shipper_Delivery, User, PersonaSistema, ShipperDeliveryPoints, Status_Orden, TrackingLogOrden, \
    ContactoProveedor, FormatoCliente, CamposDisponiblesSistema, CamposFormatosClientes
from apps.catalogo.serializers import EstadoSerializers, CiudadSerializers, TrackingLogSerializers, OrdenSerializers, \
    OrdenReporteContabilidadSerializers, ReporteOrdenesClienteSerializers
    
from .functions import dictfetchall


class HomeViewTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeViewTemplateView, self).get_context_data(**kwargs)
        idUser = self.request.user.pk
        objPersona = PersonaSistema.objects.filter(usuario_id=idUser).first()
        if not objPersona.cliente:
            arrUtilidadMes = []
            arrVentasMes = []
            arrComprasMes = []
            arrSemanasAnio = []
            today = datetime.now()
            year = today.strftime('%Y')
            conection = connection.cursor()
            # Procedimiento para obtener las vemtas, compras y utilidad en el año actual
            for x in range(1 , int(today.month) + 1):
                query_bdVenta = "select getVentaMensual({},{})".format(x,year)
                conection.execute(query_bdVenta)
                query_success = dictfetchall(conection)
                if query_success[0]['getventamensual']:
                    arrVentasMes.append(query_success[0]['getventamensual'])
                else:
                    arrVentasMes.append(0)
                query_bdCompra = "select getCostoMensual({},{})".format(x,year)
                conection.execute(query_bdCompra)
                query_success = dictfetchall(conection)
                if query_success[0]['getcostomensual']:
                    arrComprasMes.append(query_success[0]['getcostomensual'])
                else:
                    arrComprasMes.append(0)
                query_bdUtilidad = "select getUtilidadMensual({},{})".format(x,year)
                conection.execute(query_bdUtilidad)
                query_success = dictfetchall(conection)
                if query_success[0]['getutilidadmensual']:
                    arrUtilidadMes.append(query_success[0]['getutilidadmensual'])
                else:
                    arrUtilidadMes.append(0)
            
            # # Obtener la fecha actual
            fechaActual = datetime.now()
            yearActual = fechaActual.year
            arrVentaSemana = []
            # Obtener el número de la semana del año
            fechaActual = fechaActual.isocalendar()[1]
            for x in range(1, int(fechaActual) + 1):
                ventaSemanal = 0
                arrSemanasAnio.append('Semana ' + str(x))
                query_bdUtilidad = "select getVentaSemanal({})".format(x)
                conection.execute(query_bdUtilidad)
                query_success = dictfetchall(conection)
                if query_success[0]['getventasemanal'] == None:
                    arrVentaSemana.append(0)
                else:
                    arrVentaSemana.append(query_success[0]['getventasemanal'])
                # Vamos a realizar el proceso de buscar las ordenes de la semana y asi poder hacer la sumatoria
                # semanaInicio = datetime.strptime(f'{yearActual}-W{x}-1', "%Y-W%W-%w")
                # for x in range(0,7):
                #     diaSemana = semanaInicio + timedelta(days=x)
                #      # Haremos el proceso para encontrar todas las ordenes del dia tomando en cuenta las operaciones que se tienen que hacer
                #     ordenes = Orden.objects.filter(created_at__day=diaSemana.strftime('%d'),
                #                             created_at__month=diaSemana.strftime('%m'),
                #                             created_at__year=diaSemana.strftime('%Y'))
                #     for orden in ordenes:
                #         if orden.costo_cliente:
                #             ventaSemanal += int(orden.costo_cliente)
                #         if orden.costo_adicional_cliente:
                #             ventaSemanal += int(orden.costo_adicional_cliente)
                # arrVentaSemana.append(ventaSemanal)
            # Obtenemos la lista de todos clientes
            # arrCustomer = Cliente.objects.all().exclude(activo=False)
            # arrDataVentaSemanalCustomer = []
            
            # Recorremos el array de los cliente para obtener su venta semanal de la semana 0 a la semana actual del sistema
            # for customer in arrCustomer:
            #     arrVentaSemanalCustomer = []
            #     for x in range(1, int(fechaActual) + 1):
            #         ventaSemanalCustomer = 0
            #         # Vamos a realizar el proceso de buscar las ordenes de la semana y asi poder hacer la sumatoria
            #         semanaInicio = datetime.strptime(f'{yearActual}-W{x}-1', "%Y-W%W-%w")
            #         for x in range(0,7):
            #             diaSemana = semanaInicio + timedelta(days=x)
            #             # Haremos el proceso para encontrar todas las ordenes del dia tomando en cuenta las operaciones que se tienen que hacer
            #             ordenes = Orden.objects.filter(created_at__day=diaSemana.strftime('%d'),
            #                                 created_at__month=diaSemana.strftime('%m'),
            #                                 created_at__year=diaSemana.strftime('%Y'),cliente=customer)
            #             for orden in ordenes:
            #                 if orden.costo_cliente:
            #                     ventaSemanalCustomer += int(orden.costo_cliente)
            #                 if orden.costo_adicional_cliente:
            #                     ventaSemanalCustomer += int(orden.costo_cliente)
            #         arrVentaSemanalCustomer.append(ventaSemanalCustomer)
            #     arrDataVentaSemanalCustomer.append({
            #         "customer" : customer.nombre,
            #         "idCustomer" : customer.pk,
            #         "ventaSemanal" : arrVentaSemanalCustomer 
            #     })                
            context['arrSemanasAnio'] = arrSemanasAnio
            context['arrUtilidadMen'] = arrUtilidadMes
            context['arrVentasMen'] = arrVentasMes
            context['arrComprasMen'] = arrComprasMes
            context['arrVentasSemana'] = arrVentaSemana
            # context['arrVentasSemanaCustomer'] = arrDataVentaSemanalCustomer
        else:
            context['arrOrdenes'] = Orden.objects.filter(cliente_id=objPersona.cliente.pk)
        return context


#################### Procesos de APi´s ####################
class EstadosListApiView(LoginRequiredMixin, APIView):

    def get(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            pais = self.request.GET.get('pais')
            estados = Estado.objects.filter(pais_id=pais)
            serializers = EstadoSerializers(estados, many=True)
            return JsonResponse({'estados': serializers.data}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al actualizar la tabla de contactos'}, status=400)


class CuidadesListApiView(LoginRequiredMixin, APIView):

    def get(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            estado = self.request.GET.get('estado')
            cuidad = Ciudad.objects.filter(estado_id=estado)
            serializers = CiudadSerializers(cuidad, many=True)
            return JsonResponse({'ciudades': serializers.data}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al actualizar la tabla de contactos'}, status=400)


#################### Procesos para el catalago de clientes ####################
class ClienteListTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'clientes/clientes_list.html'

    def get_context_data(self, **kwargs):
        context = super(ClienteListTemplateView, self).get_context_data(**kwargs)
        context['clientes'] = Cliente.objects.all()
        return context


class ClienteNewApiView(LoginRequiredMixin, APIView):

    @transaction.atomic()
    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            nombre_cliente = self.request.POST.get('nombre_cliente')
            nombre_corto_cliente = self.request.POST.get('nombre_corto_cliente')
            nombre_contacto = self.request.POST.get('nombre_contacto')
            direccion_cliente = self.request.POST.get('direccion_cliente')
            correo_contacto = self.request.POST.get('correo_contacto')
            telefono_contacto = self.request.POST.get('telefono_contacto')

            # Validamos que no exista el cliente con el mismo nombre
            if not Cliente.objects.filter(nombre=nombre_cliente, activo=True).exists():
                # Validamos que no exista un contacto del cliente parecido con otro ya sea correo o nombre
                if not Contacto_Cliente.objects.filter(Q(nombre=nombre_cliente) | Q(correo=correo_contacto)).exists():
                    # Si ya paso la validación procedemos a realizar la creación den el modelo
                    new_cliente = Cliente.objects.create(
                        nombre=nombre_cliente,
                        nombre_corto=nombre_corto_cliente,
                        direccion=direccion_cliente,
                        register_by=self.request.user.pk
                    )
                    new_contacto_cliente = Contacto_Cliente.objects.create(
                        cliente_id=new_cliente.pk,
                        nombre=nombre_contacto,
                        correo=correo_contacto,
                        telefono=telefono_contacto,
                        register_by=self.request.user.pk
                    )
                    return JsonResponse({
                        'message': 'Cliente registrado exitosamente'
                    }, status=200)
                else:
                    return JsonResponse({'message': 'Ya existe un contacto registrado con esos datos'}, status=400)


            else:
                return JsonResponse({'message': 'Ya existe un cliente registrado con ese nombre'}, status=400)


        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar crear el cliente'}, status=400)


class ClienteActivateDeactivateApiView(LoginRequiredMixin, APIView):
    @transaction.atomic()
    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            pk_cliente = self.request.POST.get('cliente_pk')
            cliente = Cliente.objects.get(pk=pk_cliente)
            deactivate = self.request.POST.get('deactivate').capitalize()
            # Validamos si hay que activar o desactivar el cliente
            if bool(deactivate):
                # Vamos desactivar el cliente
                cliente.activo = False
                cliente.save()
                # Ahora vamos a desactivar a todos los contactos de ese cliente
                contactos = Contacto_Cliente.objects.filter(cliente=cliente)
                for contacto in contactos:
                    contacto.activo = False
                    contacto.save()
                return JsonResponse({
                    'message': 'Cliente desactivado exitosamente'
                }, status=200)
            else:

                # Vamos activar el cliente
                cliente.activo = True
                cliente.save()
                # Ahora vamos a activar a todos los contactos de ese cliente
                contactos = Contacto_Cliente.objects.filter(cliente=cliente)
                for contacto in contactos:
                    contacto.activo = True
                    contacto.save()
                return JsonResponse({
                    'message': 'Cliente activado exitosamente'
                }, status=200)


        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar crear el cliente'}, status=400)


class ClienteContactoSaveEditApiView(LoginRequiredMixin, APIView):

    @transaction.atomic()
    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            pk_cliente = self.request.POST.get('cliente')
            pk_contacto = self.request.POST.get('contacto')
            nombre_contacto = self.request.POST.get('nombre_new_contacto')
            correo_contacto = self.request.POST.get('correo_new_contacto')
            telefono_contacto = self.request.POST.get('telefono_new_contacto')
            if not pk_contacto:
                # Validamos que no exista un contacto del cliente parecido con otro ya sea correo o nombre
                if not Contacto_Cliente.objects.filter(
                        Q(nombre=nombre_contacto) | Q(correo=correo_contacto) | Q(telefono=telefono_contacto)).exists():
                    # Crearemos el contacto agregando su debida validación
                    new_contacto_cliente = Contacto_Cliente.objects.create(
                        cliente_id=pk_cliente,
                        nombre=nombre_contacto,
                        correo=correo_contacto,
                        telefono=telefono_contacto,
                        register_by=self.request.user.pk
                    )
                    return JsonResponse({
                        'message': 'Contacto creado exitosamente'
                    }, status=200)
                else:
                    return JsonResponse({'message': 'Ya existe un contacto creado con esos datos'}, status=400)
            else:
                # Obtenemos el contacto por que es actualización
                contacto = Contacto_Cliente.objects.get(pk=pk_contacto)
                # Validamos que no exista ninun registrop
                if not Contacto_Cliente.objects.filter(
                        Q(nombre=nombre_contacto) | Q(correo=correo_contacto) | Q(telefono=telefono_contacto)).exclude(
                    pk=contacto.pk).exists():
                    # Actualizamos los datos corresponeinted del contacto
                    contacto.nombre = nombre_contacto
                    contacto.correo = correo_contacto
                    contacto.telefono = telefono_contacto
                    contacto.save()
                    return JsonResponse({
                        'message': 'Contacto actualizado exitosamente'
                    }, status=200)
                else:
                    return JsonResponse({'message': 'Ya existe un contacto creado con esos datos'}, status=400)

        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al realizar el proceso actual'}, status=400)


class ClienteContactoListaApiView(LoginRequiredMixin, APIView):

    def get(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            pk_cliente = self.request.GET.get('cliente')
            cliente = Cliente.objects.get(pk=pk_cliente)
            return JsonResponse({'contactos': cliente.get_contactos()}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al actualizar la tabla de contactos'}, status=400)


class ClienteContactoEliminarApiView(LoginRequiredMixin, APIView):

    @transaction.atomic()
    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            pk_contacto = self.request.POST.get('contacto')
            contacto = Contacto_Cliente.objects.get(pk=pk_contacto)
            contacto.delete()
            return JsonResponse({'message': 'Contacto eliminado correctamente'}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar eliminar el contacto'}, status=400)


#################### Procesos para el catalogo de provedores ####################

class ProveedoresListTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'proveedores/proveedores_list.html'

    def get_context_data(self, **kwargs):
        context = super(ProveedoresListTemplateView, self).get_context_data(**kwargs)
        context['proveedores'] = Proveedor.objects.all()
        context['paises'] = Pais.objects.all().exclude(activo=False)
        return context


class ProveedoresNewApiView(LoginRequiredMixin, APIView):

    @transaction.atomic()
    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            nombre_proveedor = self.request.POST.get('nombre_proveedor')
            nombre_corto_proveedor = self.request.POST.get('nombre_corto_proveedor')
            # direccion_proveedor = self.request.POST.get('direccion_proveedor')
            calle_proveedor = self.request.POST.get('calle_proveedor')
            numero_proveedor = self.request.POST.get('numero_proveedor')
            cp_proveedor = self.request.POST.get('cp_proveedor')
            ciudad = self.request.POST.get('ciudad_proveedor')
            listContactos = self.request.POST.get('listContactos')

            # Validamos que no exista un proveedor  con el mismo nombre
            if not Proveedor.objects.filter(nombre=nombre_proveedor, activo=True).exists():
                # Validamos que no exista un contacto del cliente parecido con otro ya sea correo o nombre
                # Si ya paso la validación procedemos a realizar la creación den el modelo
                new_proveedor = Proveedor.objects.create(
                    nombre=nombre_proveedor,
                    nombre_corto=nombre_corto_proveedor,
                    # direccion=direccion_proveedor,
                    calle=calle_proveedor,
                    numero=numero_proveedor,
                    cp=cp_proveedor,
                    cuidad_id=ciudad,
                    register_by=self.request.user.pk
                )
                if listContactos:
                    for contacto in json.loads(listContactos):
                        print(contacto)
                        new_contacto = ContactoProveedor.objects.create(
                            nombre=contacto['nombre'],
                            proveedor=new_proveedor,
                            puesto=contacto['puesto'],
                            celular=contacto['numero'],
                            email=contacto['correo'],
                            register_by=self.request.user.pk
                        )

                return JsonResponse({
                    'message': 'Proveedor registrado exitosamente'
                }, status=200)
            else:
                return JsonResponse({'message': 'Ya existe un proveedor registrado con ese nombre'}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar crear el proveedor'}, status=400)


class ProveedoresNewCargaMasiva(LoginRequiredMixin, View):

    @transaction.atomic()
    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            archivo = self.request.FILES["input-file"]
            csvf = StringIO(archivo.read().decode())
            reader = csv.reader(csvf, delimiter=",")
            headers = next(reader)
            headers_error = ['Proveedor', 'Nombre Corto', 'Direccion', 'Mensaje']
            errores = []

            for row in reader:
                if row[0] and row[2]:
                    nombre_proveedor = row[0]
                    nombre_corto_proveedor = row[1]
                    direccion_proveedor = row[2]
                    # Validamos que no exista un proveedor  con el mismo nombre
                    if not Proveedor.objects.filter(nombre=nombre_proveedor.upper(), activo=True).exists():
                        # Validamos que no exista un contacto del cliente parecido con otro ya sea correo o nombre
                        # Si ya paso la validación procedemos a realizar la creación den el modelo
                        new_proveedor = Proveedor.objects.create(
                            nombre=nombre_proveedor.upper(),
                            nombre_corto=nombre_corto_proveedor.upper(),
                            direccion=direccion_proveedor.upper(),
                            register_by=self.request.user.pk
                        )
                        errores.append([
                            nombre_proveedor,
                            nombre_corto_proveedor,
                            direccion_proveedor,
                            'Proveedor Registrado Exitosamente'
                        ])
                        continue
                    else:
                        errores.append([
                            nombre_proveedor,
                            nombre_corto_proveedor,
                            direccion_proveedor,
                            'Ya existe un proveedor con ese nombre'
                        ])
                        continue
            with open(f'{settings.MEDIA_ROOT}cargamasiva/error_carga_masiva.csv', 'w', newline="") as file:
                csvwriter = csv.writer(file)  # 2. create a csvwriter object
                csvwriter.writerow(headers_error)  # 4. write the header
                csvwriter.writerows(errores)  # 5. write the rest of the data
            messages.success(self.request, 'Carga masiva completada', extra_tags="¡Éxito!")
            return HttpResponseRedirect(reverse('catalogo:proveedores-list'))
        except Exception as e:
            messages.error(self.request, 'Hubo un error al hacer la carga masiva', extra_tags="¡Error!")
            return HttpResponseRedirect(reverse('catalogo:proveedores-list'))


class ProveedoresEditApiView(LoginRequiredMixin, APIView):

    @transaction.atomic()
    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            pk_proveedor = self.request.POST.get('proveedor')
            nombre_proveedor = self.request.POST.get('nombre_proveedor_update')
            nombre_corto_proveedor = self.request.POST.get('nombre_corto_proveedor_update')
            # direccion_proveedor = self.request.POST.get('direccion_proveedor_update')
            calle_proveedor = self.request.POST.get('calle_proveedor_update')
            numero_proveedor = self.request.POST.get('numero_proveedor_update')
            cp_proveedor = self.request.POST.get('cp_proveedor_update')
            ciudad = self.request.POST.get('ciudad_proveedor_update')
            proveedor = Proveedor.objects.get(pk=pk_proveedor)
            listContactos = self.request.POST.get('listContactos')
            # Validamos que no exista un proveedor  con el mismo nombre
            if not Proveedor.objects.filter(nombre=nombre_proveedor, activo=True).exclude(pk=pk_proveedor).exists():
                # Validamos que no exista un contacto del cliente parecido con otro ya sea correo o nombre
                # Si ya paso la validación procedemos a realizar la creación den el modelo
                proveedor.nombre = nombre_proveedor
                proveedor.nombre_corto = nombre_corto_proveedor
                # proveedor.direccion = direccion_proveedor
                proveedor.cuidad_id = ciudad
                proveedor.cp = cp_proveedor
                proveedor.numero = numero_proveedor
                proveedor.calle = calle_proveedor
                proveedor.save()
                arrContactosProveedor = ContactoProveedor.objects.filter(proveedor=proveedor)
                arrContactosProveedor.delete()
                if listContactos:
                    for contacto in json.loads(listContactos):
                        print(contacto)
                        new_contacto = ContactoProveedor.objects.create(
                            nombre=contacto['nombre'],
                            proveedor=proveedor,
                            puesto=contacto['puesto'],
                            celular=contacto['numero'],
                            email=contacto['correo'],
                            register_by=self.request.user.pk
                        )

                return JsonResponse({
                    'message': 'Proveedor actualizado exitosamente'
                }, status=200)
            else:
                return JsonResponse({'message': 'Ya existe un proveedor registrado con ese nombre'}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar crear el proveedor'}, status=400)


class ProveedorActivateDeactivateApiView(LoginRequiredMixin, APIView):
    @transaction.atomic()
    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            pk_proveedor = self.request.POST.get('proveedor_pk')
            proveedor = Proveedor.objects.get(pk=pk_proveedor)
            deactivate = self.request.POST.get('deactivate').capitalize()
            # Validamos si hay que activar o desactivar el cliente
            if bool(deactivate):
                # Vamos desactivar el proveedor
                proveedor.activo = False
                proveedor.save()
                return JsonResponse({
                    'message': 'Proveedor desactivado exitosamente'
                }, status=200)
            else:

                # Vamos activar el cliente
                proveedor.activo = True
                proveedor.save()
                return JsonResponse({
                    'message': 'Proveedor activado exitosamente'
                }, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar realizar el proceso actual'}, status=400)


#################### Procesos para el catalogo de productos ####################

class ProductosListTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'productos/productos_list.html'

    def get_context_data(self, **kwargs):
        context = super(ProductosListTemplateView, self).get_context_data(**kwargs)
        context['productos'] = Producto.objects.all()
        return context


class ProductoNewApiView(LoginRequiredMixin, APIView):

    @transaction.atomic()
    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            nombre_producto = self.request.POST.get('nombre_producto')
            nombre_corto_producto = self.request.POST.get('nombre_corto_producto')
            sku_producto = self.request.POST.get('sku_producto')

            # Validamos que no exista un producto con el mismo nombre  con el mismo nombre
            if not Producto.objects.filter(nombre=nombre_producto, activo=True).exists():
                # Validamos que no exista un producto con el sku de otro producto
                if not Producto.objects.filter(sku=sku_producto, activo=True).exists():
                    # Si ya paso la validación procedemos a realizar la creación den el modelo
                    new_producto = Producto.objects.create(
                        nombre=nombre_producto,
                        nombre_corto=nombre_corto_producto,
                        sku=sku_producto,
                        register_by=self.request.user.pk
                    )
                    return JsonResponse({
                        'message': 'Producto registrado exitosamente'
                    }, status=200)
                else:
                    return JsonResponse({'message': 'Ya existe un producto registrado con ese sku'}, status=400)

            else:
                return JsonResponse({'message': 'Ya existe un producto registrado con ese nombre'}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar crear el producto'}, status=400)


class ProductoNewCargaMasiva(LoginRequiredMixin, View):

    @transaction.atomic()
    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            archivo = self.request.FILES["input-file"]
            csvf = StringIO(archivo.read().decode())
            reader = csv.reader(csvf, delimiter=",")
            headers = next(reader)
            headers_error = ['Nombre', 'Nombre Corto', 'SKU', 'Mensaje Error']
            errores = []

            for row in reader:
                if row[0] and row[2]:
                    nombre_producto = row[0]
                    nombre_corto_producto = row[1]
                    sku_producto = row[2]
                    # Validamos que no exista un producto con el mismo nombre  con el mismo nombre
                    if not Producto.objects.filter(nombre=nombre_producto, activo=True).exists():
                        # Validamos que no exista un producto con el sku de otro producto
                        if not Producto.objects.filter(sku=sku_producto, activo=True).exists():
                            # Si ya paso la validación procedemos a realizar la creación den el modelo
                            new_producto = Producto.objects.create(
                                nombre=nombre_producto,
                                nombre_corto=nombre_corto_producto,
                                sku=sku_producto,
                                register_by=self.request.user.pk
                            )
                            errores.append([
                                nombre_corto_producto,
                                nombre_producto,
                                sku_producto,
                                'Producto Registrado Exitosamente'
                            ])
                        else:
                            errores.append([
                                nombre_producto,
                                nombre_corto_producto,
                                sku_producto,
                                'Ya existe un producto registrado con ese sku'
                            ])
                            continue
                    else:
                        errores.append([
                            nombre_producto,
                            nombre_corto_producto,
                            sku_producto,
                            'Ya existe un producto registrado con ese nombre'
                        ])
                        continue
            with open(f'{settings.MEDIA_ROOT}cargamasiva/error_carga_masiva.csv', 'w', newline="") as file:
                csvwriter = csv.writer(file)  # 2. create a csvwriter object
                csvwriter.writerow(headers_error)  # 4. write the header
                csvwriter.writerows(errores)  # 5. write the rest of the data
            messages.success(self.request, 'Carga masiva completada', extra_tags="¡Éxito!")
            return HttpResponseRedirect(reverse('catalogo:productos-list'))
        except Exception as e:
            messages.error(self.request, 'Hubo un error al hacer la carga masiva', extra_tags="¡Error!")
            return HttpResponseRedirect(reverse('catalogo:productos-list'))


class ProductoEditApiView(LoginRequiredMixin, APIView):

    @transaction.atomic()
    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            pk_producto = self.request.POST.get('producto')
            nombre_producto = self.request.POST.get('nombre_producto_update')
            nombre_corto_producto = self.request.POST.get('nombre_corto_producto_update')
            sku_producto = self.request.POST.get('sku_producto_update')

            producto = Producto.objects.get(pk=pk_producto)
            # Validamos que no exista un proveedor  con el mismo nombre
            if not Proveedor.objects.filter(nombre=nombre_producto, activo=True).exclude(pk=pk_producto).exists():
                # Validamos que no exista un contacto del cliente parecido con otro ya sea correo o nombre
                # Si ya paso la validación procedemos a realizar la creación den el modelo
                producto.nombre = nombre_producto
                producto.nombre_corto = nombre_corto_producto
                producto.sku = sku_producto
                producto.save()
                return JsonResponse({
                    'message': 'Producto actualizado exitosamente'
                }, status=200)
            else:
                return JsonResponse({'message': 'Ya existe un producto registrado con ese nombre'}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar actualizar el producto'}, status=400)


class ProductoActivateDeactivateApiView(LoginRequiredMixin, APIView):
    @transaction.atomic()
    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            pk_producto = self.request.POST.get('producto_pk')
            producto = Producto.objects.get(pk=pk_producto)
            deactivate = self.request.POST.get('deactivate').capitalize()
            # Validamos si hay que activar o desactivar el cliente
            if bool(deactivate):
                # Vamos desactivar el proveedor
                producto.activo = False
                producto.save()
                return JsonResponse({
                    'message': 'Producto desactivado exitosamente'
                }, status=200)
            else:
                # Vamos activar el cliente
                producto.activo = True
                producto.save()
                return JsonResponse({
                    'message': 'Producto activado exitosamente'
                }, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar realizar el proceso actual'}, status=400)


#################### Procesos para el catalogo de shipper ####################

class ShipperListTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'shipper/shipper_list.html'

    def get_context_data(self, **kwargs):
        context = super(ShipperListTemplateView, self).get_context_data(**kwargs)
        context['shippers'] = Shipper_Delivery.objects.all().exclude(tipo=2)
        context['paises'] = Pais.objects.all().exclude(activo=False)
        return context


class ShipperCreateApiView(LoginRequiredMixin, APIView):

    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            nombre_shipper = self.request.POST.get('nombre_shipper')
            contacto_shipper = self.request.POST.get('contacto_shipper')
            telefono_contacto_shipper = self.request.POST.get('telefono_contacto_shipper')
            email_contacto_shipper = self.request.POST.get('email_contacto_shipper')
            direccion_contacto_shipper = self.request.POST.get('direccion_contacto_shipper')
            cp_zip_contacto_shipper = self.request.POST.get('cp_zip_contacto_shipper')
            ciudad_shipper = self.request.POST.get('ciudad_shipper')
            shipper_delivery = self.request.POST.get('shipper_delivery')
            # Validamos que no existe algun shipper o delivery con ese mismo nombre
            if not Shipper_Delivery.objects.filter(nombre=nombre_shipper).exclude(tipo=3).exists():
                # Validamos que no exista algun shipper o delivery con ese mismo contacto
                if not Shipper_Delivery.objects.filter(c_nombre=contacto_shipper).exclude(tipo=3).exists():
                    # Validamos que no exista algun shippero o delivery con el mismo número
                    if not Shipper_Delivery.objects.filter(c_telefono=telefono_contacto_shipper).exclude(
                            tipo=3).exists():
                        # Validamos que no exista algun shipper o delivery con el mismo email
                        if not Shipper_Delivery.objects.filter(c_email=email_contacto_shipper).exclude(
                                tipo=3).exists():
                            new_shipper = Shipper_Delivery.objects.create(
                                nombre=nombre_shipper,
                                c_nombre=contacto_shipper,
                                c_telefono=telefono_contacto_shipper,
                                c_email=email_contacto_shipper,
                                direccion=direccion_contacto_shipper,
                                cp=cp_zip_contacto_shipper,
                                cuidad_id=ciudad_shipper,
                                register_by=self.request.user.pk
                            )
                            if shipper_delivery:
                                new_shipper.tipo = 3
                            else:
                                new_shipper.tipo = 1
                            new_shipper.save()
                            return JsonResponse({
                                'message': 'Shipper Points registrado exitosamente'
                            }, status=200)
                        else:
                            return JsonResponse(
                                {'message': 'Ya Existe un shipper o delivery con ese correo électronico'},
                                status=400)
                    else:
                        return JsonResponse({'message': 'Ya Existe un shipper o delivery con ese telefono'},
                                            status=400)
                else:
                    return JsonResponse({'message': 'Ya Existe un shipper o delivery con ese nombre de contacto'},
                                        status=400)

            else:
                return JsonResponse({'message': 'Ya Existe un shipper o delivery con ese mismo nombre'}, status=400)

        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar realizar el proceso actual'}, status=400)


class ShipperEditApiView(LoginRequiredMixin, APIView):

    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            shipper_id = self.request.POST.get('shipper')
            nombre_shipper = self.request.POST.get('nombre_shipper_update')
            contacto_shipper = self.request.POST.get('contacto_shipper_update')
            telefono_contacto_shipper = self.request.POST.get('telefono_contacto_shipper_update')
            email_contacto_shipper = self.request.POST.get('email_contacto_shipper_update')
            direccion_contacto_shipper = self.request.POST.get('direccion_contacto_shipper_update')
            cp_zip_contacto_shipper = self.request.POST.get('cp_zip_contacto_shipper_update')
            ciudad_shipper = self.request.POST.get('ciudad_shipper_update')
            shipper_delivery = self.request.POST.get('shipper_delivery_update')
            # Validamos que no existe algun shipper o delivery con ese mismo nombre
            if not Shipper_Delivery.objects.filter(nombre=nombre_shipper).exclude(pk=shipper_id).exists():
                # Validamos que no exista algun shipper o delivery con ese mismo contacto
                if not Shipper_Delivery.objects.filter(c_nombre=contacto_shipper).exclude(pk=shipper_id).exists():
                    # Validamos que no exista algun shippero o delivery con el mismo número
                    if not Shipper_Delivery.objects.filter(c_telefono=telefono_contacto_shipper).exclude(
                            pk=shipper_id).exists():
                        # Validamos que no exista algun shipper o delivery con el mismo email
                        if not Shipper_Delivery.objects.filter(c_email=email_contacto_shipper).exclude(
                                pk=shipper_id).exists():
                            shipper_update = Shipper_Delivery.objects.get(pk=shipper_id)
                            shipper_update.nombre = nombre_shipper
                            shipper_update.c_nombre = contacto_shipper
                            shipper_update.c_telefono = telefono_contacto_shipper
                            shipper_update.c_email = email_contacto_shipper
                            shipper_update.direccion = direccion_contacto_shipper
                            shipper_update.cp = cp_zip_contacto_shipper
                            shipper_update.cuidad_id = ciudad_shipper
                            if shipper_delivery:
                                shipper_update.tipo = 3
                            else:
                                shipper_update.tipo = 1
                            shipper_update.save()
                            return JsonResponse({
                                'message': 'Shipper Points actualizado exitosamente'
                            }, status=200)
                        else:
                            return JsonResponse(
                                {'message': 'Ya Existe un shipper o delivery con ese correo électronico'},
                                status=400)
                    else:
                        return JsonResponse({'message': 'Ya Existe un shipper o delivery con ese telefono'},
                                            status=400)
                else:
                    return JsonResponse({'message': 'Ya Existe un shipper o delivery con ese nombre de contacto'},
                                        status=400)

            else:
                return JsonResponse({'message': 'Ya Existe un shipper o delivery con ese mismo nombre'}, status=400)

        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar realizar el proceso actual'}, status=400)


class ShipperDeliveryActivateDeactivateApiView(LoginRequiredMixin, APIView):

    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            pk = self.request.POST.get('pk')
            shipper_delivery = Shipper_Delivery.objects.get(pk=pk)
            deactivate = self.request.POST.get('deactivate').capitalize()
            # Validamos si hay que activar o desactivar el cliente
            if bool(deactivate):
                # Vamos desactivar el proveedor
                shipper_delivery.activo = False
                shipper_delivery.save()
                return JsonResponse({
                    'message': 'Desactivado exitosamente'
                }, status=200)
            else:
                # Vamos activar el cliente
                shipper_delivery.activo = True
                shipper_delivery.save()
                return JsonResponse({
                    'message': 'Activado exitosamente'
                }, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar realizar el proceso actual'}, status=400)


#################### Procesos para el catalogo de delivery ####################

class DeliveryListTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'delivery/delivery_list.html'

    def get_context_data(self, **kwargs):
        context = super(DeliveryListTemplateView, self).get_context_data(**kwargs)
        context['deliverys'] = Shipper_Delivery.objects.all().exclude(tipo=1)
        context['paises'] = Pais.objects.all().exclude(activo=False)
        return context


class DeliveryCreateApiView(LoginRequiredMixin, APIView):

    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            nombre_delivery = self.request.POST.get('nombre_delivery')
            contacto_delivery = self.request.POST.get('contacto_delivery')
            telefono_contacto_delivery = self.request.POST.get('telefono_contacto_delivery')
            email_contacto_delivery = self.request.POST.get('email_contacto_delivery')
            direccion_contacto_delivery = self.request.POST.get('direccion_contacto_delivery')
            cp_zip_contacto_delivery = self.request.POST.get('cp_zip_contacto_delivery')
            ciudad_delivery = self.request.POST.get('ciudad_delivery')
            shipper_delivery = self.request.POST.get('shipper_delivery')
            # Validamos que no existe algun delivery o delivery con ese mismo nombre
            if not Shipper_Delivery.objects.filter(nombre=nombre_delivery).exclude(tipo=3).exists():
                # Validamos que no exista algun delivery o delivery con ese mismo contacto
                if not Shipper_Delivery.objects.filter(c_nombre=contacto_delivery).exclude(tipo=3).exists():
                    # Validamos que no exista algun deliveryo o delivery con el mismo número
                    if not Shipper_Delivery.objects.filter(c_telefono=telefono_contacto_delivery).exclude(
                            tipo=3).exists():
                        # Validamos que no exista algun delivery o delivery con el mismo email
                        if not Shipper_Delivery.objects.filter(c_email=email_contacto_delivery).exclude(
                                tipo=3).exists():
                            new_delivery = Shipper_Delivery.objects.create(
                                nombre=nombre_delivery,
                                c_nombre=contacto_delivery,
                                c_telefono=telefono_contacto_delivery,
                                c_email=email_contacto_delivery,
                                direccion=direccion_contacto_delivery,
                                cp=cp_zip_contacto_delivery,
                                cuidad_id=ciudad_delivery,
                                register_by=self.request.user.pk
                            )
                            if shipper_delivery:
                                new_delivery.tipo = 3
                            else:
                                new_delivery.tipo = 2
                            new_delivery.save()
                            return JsonResponse({
                                'message': 'Delivery Points registrado exitosamente'
                            }, status=200)
                        else:
                            return JsonResponse(
                                {'message': 'Ya Existe un shipper o delivery con ese correo électronico'},
                                status=400)
                    else:
                        return JsonResponse({'message': 'Ya Existe un shipper o delivery con ese telefono'},
                                            status=400)
                else:
                    return JsonResponse({'message': 'Ya Existe un shipper o delivery con ese nombre de contacto'},
                                        status=400)

            else:
                return JsonResponse({'message': 'Ya Existe un shipper o delivery con ese mismo nombre'}, status=400)

        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar realizar el proceso actual'}, status=400)


class DeliveryEditApiView(LoginRequiredMixin, APIView):

    def post(self, request):
        try:
            # Recibimos los valores enviados a traves del ajax
            delivery_id = self.request.POST.get('delivery')
            nombre_delivery = self.request.POST.get('nombre_delivery_update')
            contacto_delivery = self.request.POST.get('contacto_delivery_update')
            telefono_contacto_delivery = self.request.POST.get('telefono_contacto_delivery_update')
            email_contacto_delivery = self.request.POST.get('email_contacto_delivery_update')
            direccion_contacto_delivery = self.request.POST.get('direccion_contacto_delivery_update')
            cp_zip_contacto_delivery = self.request.POST.get('cp_zip_contacto_delivery_update')
            ciudad_delivery = self.request.POST.get('ciudad_delivery_update')
            shipper_delivery = self.request.POST.get('shipper_delivery_update')
            # Validamos que no existe algun delivery o delivery con ese mismo nombre
            if not Shipper_Delivery.objects.filter(nombre=nombre_delivery).exclude(pk=delivery_id).exists():
                # Validamos que no exista algun delivery o delivery con ese mismo contacto
                if not Shipper_Delivery.objects.filter(c_nombre=contacto_delivery).exclude(pk=delivery_id).exists():
                    # Validamos que no exista algun deliveryo o delivery con el mismo número
                    if not Shipper_Delivery.objects.filter(c_telefono=telefono_contacto_delivery).exclude(
                            pk=delivery_id).exists():
                        # Validamos que no exista algun delivery o delivery con el mismo email
                        if not Shipper_Delivery.objects.filter(c_email=email_contacto_delivery).exclude(
                                pk=delivery_id).exists():
                            delivery_update = Shipper_Delivery.objects.get(pk=delivery_id)
                            delivery_update.nombre = nombre_delivery
                            delivery_update.c_nombre = contacto_delivery
                            delivery_update.c_telefono = telefono_contacto_delivery
                            delivery_update.c_email = email_contacto_delivery
                            delivery_update.direccion = direccion_contacto_delivery
                            delivery_update.cp = cp_zip_contacto_delivery
                            delivery_update.cuidad_id = ciudad_delivery
                            if shipper_delivery:
                                delivery_update.tipo = 3
                            else:
                                delivery_update.tipo = 2
                            delivery_update.save()
                            return JsonResponse({
                                'message': 'Delivery Points actualizado exitosamente'
                            }, status=200)
                        else:
                            return JsonResponse(
                                {'message': 'Ya Existe un shipper o delivery con ese correo électronico'},
                                status=400)
                    else:
                        return JsonResponse({'message': 'Ya Existe un shipper o delivery con ese telefono'},
                                            status=400)
                else:
                    return JsonResponse({'message': 'Ya Existe un shipper o delivery con ese nombre de contacto'},
                                        status=400)

            else:
                return JsonResponse({'message': 'Ya Existe un shipper o delivery con ese mismo nombre'}, status=400)

        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar realizar el proceso actual'}, status=400)


#################### Procesos para el catalogo de ordenes ####################

class OrdenesTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'ordenes/ordenes_list.html'

    def get_context_data(self, **kwargs):
        context = super(OrdenesTemplateView, self).get_context_data(**kwargs)
        if not self.request.GET.get('ordenes'):
            context['ordenes'] = Orden.objects.filter().exclude(Q(status_orden=16) | Q(status_orden=17)).order_by('-pk')
            context['filtro'] = 1
        else:
            if self.request.GET.get('ordenes') == '16':
                context['ordenes'] = Orden.objects.filter(status_orden=self.request.GET.get('ordenes')).order_by('-pk')
                context['filtro'] = 2
            else:
                context['ordenes'] = Orden.objects.filter().order_by('-pk')
                context['filtro'] = 3
        context['status'] = Status_Orden.objects.all().exclude(pk=1).order_by('descripcion')
        return context


class OrdenesClienteTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'ordenes/ordenes_list_customer.html'

    def get_context_data(self, **kwargs):
        context = super(OrdenesClienteTemplateView, self).get_context_data(**kwargs)
        # Obtenemos el cliente de quien esta consultando para poder obtener todas las ordenes registradas para el
        persona = PersonaSistema.objects.get(usuario_id=self.request.user.pk)
        # Obtenemos las ordenes registradas para el cliente
        if self.request.GET.get('ordenes'):
            context['ordenes'] = Orden.objects.filter(cliente=persona.cliente).order_by('-pk')
            context['filtro'] = 2
        else:
            context['ordenes'] = Orden.objects.filter(cliente=persona.cliente).exclude(status_orden_id=16).order_by(
                '-pk')
            context['filtro'] = 1
        print(Orden.objects.filter(cliente=persona.cliente).order_by('-pk'))
        return context


class OrdenContableTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'ordenes/ordenes_list.html'

    def get_context_data(self, **kwargs):
        context = super(OrdenContableTemplateView, self).get_context_data(**kwargs)
        conection = connection.cursor()
        if self.request.GET.get('ordenes'):
            if self.request.GET.get('ordenes') == '100':
                context['filtro'] = 4
                query_bd = "select getOrdenesAllSF()"
                conection.execute(query_bd)
                query_success = dictfetchall(conection)
                print(query_success[0]['getordenesallsf'])
                context['ordenes'] = query_success[0]['getordenesallsf']
            else:
                query_bd = "select getOrdenesAll('{}')".format(self.request.GET.get('ordenes'))
                context['filtro'] = 2
                conection.execute(query_bd)
                query_success = dictfetchall(conection)
                context['ordenes'] = query_success[0]['getordenesall']
        if self.request.GET.get('all'):
            query_bd = "select getOrdenesAll(null)"
            conection.execute(query_bd)
            query_success = dictfetchall(conection) 
            context['ordenes'] = query_success[0]['getordenesall']
            context['filtro'] = 3
        
        context['status'] = Status_Orden.objects.all().exclude(pk=1).order_by('descripcion')
        context['contabilidad'] = True
        return context


class OrdenCrearTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'ordenes/orden_add_edit.html'

    def get_context_data(self, **kwargs):
        context = super(OrdenCrearTemplateView, self).get_context_data(**kwargs)
        context['clientes'] = Cliente.objects.all().exclude(activo=False)
        context['proveedores'] = Proveedor.objects.all().exclude(activo=False)
        context['productos'] = Producto.objects.all().exclude(activo=False)
        context['shippers'] = Shipper_Delivery.objects.all().exclude(tipo=2)
        context['deliverys'] = Shipper_Delivery.objects.all().exclude(tipo=1)
        return context

    @transaction.atomic()
    def post(self, request):
        try:
            # Obtenemos los datos enviados a traves de la petición AJAX
            points = self.request.POST.get('points')
            cliente_orden = self.request.POST.get('cliente_orden')
            costo_cliente_orden = self.request.POST.get('costo_cliente_orden')
            costo_adicional_cliente_orden = self.request.POST.get('costo_adicional_cliente_orden')
            wo_orden = self.request.POST.get('wo_orden')
            proveedor_orden = self.request.POST.get('proveedor_orden')
            costo_proveedor_orden = self.request.POST.get('costo_proveedor_orden')
            costo_adicional_proveedor_orden = self.request.POST.get('costo_adicional_proveedor_orden')
            eq_type_orden = self.request.POST.get('eq_type_orden')
            tipo_cambio_orden = self.request.POST.get('tipo_cambio_orden')
            adicional_pedimento = self.request.POST.get('adicional_pedimento')
            direccion_origen = self.request.POST.get('direccion_origen')
            direccion_destino = self.request.POST.get('direccion_destino')
            adicional_pro = self.request.POST.get('adicional_pro')
            adicional_load = self.request.POST.get('adicional_load')
            adicional_mx_truck_num = self.request.POST.get('adicional_mx_truck_num')
            adicional_us_truck_num = self.request.POST.get('adicional_us_truck_num')
            adicional_load_type = self.request.POST.get('adicional_load_type')
            adicional_mx_plate_num = self.request.POST.get('adicional_mx_plate_num')
            adicional_us_plate_num = self.request.POST.get('adicional_us_plate_num')
            adicional_realase = self.request.POST.get('adicional_realase')
            adicional_mx_driver_one = self.request.POST.get('adicional_mx_driver_one')
            adicional_mx_driver_two = self.request.POST.get('adicional_mx_driver_two')
            adicional_vin = self.request.POST.get('adicional_vin')
            adicional_lms = self.request.POST.get('adicional_lms')
            adicional_us_driver_one = self.request.POST.get('adicional_us_driver_one')
            adicional_invoice = self.request.POST.get('adicional_invoice')
            adicional_mx_driver_phone_one = self.request.POST.get('adicional_mx_driver_phone_one')
            adicional_us_driver_two = self.request.POST.get('adicional_us_driver_two')
            adicional_invoice_date = self.request.POST.get('adicional_invoice_date')
            adicional_empty_truck = self.request.POST.get('adicional_empty_truck')
            adicional_us_driver_phone_one = self.request.POST.get('adicional_us_driver_phone_one')
            adicional_notif_docs = self.request.POST.get('adicional_notif_docs')
            adicional_cma = self.request.POST.get('adicional_cma')
            adicional_maniobras = self.request.POST.get('adicional_maniobras')
            adicional_estancias = self.request.POST.get('adicional_estancias')
            adicional_otros = self.request.POST.get('adicional_otros')
            adicional_arrival = self.request.POST.get('adicional_arrival')
            adicional_loading_time = self.request.POST.get('adicional_loading_time')
            adicional_waiting = self.request.POST.get('adicional_waiting')
            adicional_crossing_time = self.request.POST.get('adicional_crossing_time')
            adicional_serie = self.request.POST.get('adicional_serie')
            adicional_folio = self.request.POST.get('adicional_folio')
            adicional_uuid = self.request.POST.get('adicional_uuid')
            # Campos para la nueva parte de contabilidad
            cliente_factura = self.request.POST.get('cliente_factura')
            cliente_factura_fecha = self.request.POST.get('cliente_factura_fecha')
            cliente_pago_fecha = self.request.POST.get('cliente_pago_fecha')
            cliente_cantidad = self.request.POST.get('cliente_cantidad')
            factoraje_fecha_deposito = self.request.POST.get('factoraje_fecha_deposito')
            factoraje_monto = self.request.POST.get('factoraje_monto')
            saldo = self.request.POST.get('saldo')
            fecha_pago = self.request.POST.get('fecha_pago')
            monto_pago = self.request.POST.get('monto_pago')
            pago_factoraje_fecha = self.request.POST.get('pago_factoraje_fecha')
            pago_factoraje_referencia = self.request.POST.get('pago_factoraje_referencia')
            pago_factoraje_monto = self.request.POST.get('pago_factoraje_monto')
            proovedor_factura = self.request.POST.get('proovedor_factura')
            proovedor_monto = self.request.POST.get('proovedor_monto')
            proveedor_pago_fecha = self.request.POST.get('proveedor_pago_fecha')
            proveedor_pago_monto = self.request.POST.get('proveedor_pago_monto')
            fecha_orden = self.request.POST.get('fecha_orden')

            # Nuevos Datos para lo de los datos de la tabla

            esj_po = self.request.POST.get('esj_po')
            flatbed = self.request.POST.get('flatbed')
            carrier_mx = self.request.POST.get('carrier_mx')
            carrier_usa = self.request.POST.get('carrier_usa')
            loading_warehouse = self.request.POST.get('loading_warehouse')
            departure_esj = self.request.POST.get('departure_esj')
            arrival_juarez = self.request.POST.get('arrival_juarez')
            arrival_el_paso = self.request.POST.get('arrival_el_paso')
            departure_usa = self.request.POST.get('departure_usa')
            arrival_destination = self.request.POST.get('arrival_destination')
            # Procederemos a crear la orden con todos los campos recibidos para despues recorrer los points y poder crear los poinst de acuerdo a la orden
            
            # Procedemos a validar si viene el campo adicional proveedor y adicional cliente para que en caos de que no sea asi, asignar 0
            adicional_cliente = 0
            if costo_adicional_cliente_orden:
                adicional_cliente = costo_adicional_cliente_orden
                
            adicional_proveedor = 0
            if costo_adicional_proveedor_orden:
                adicional_proveedor = costo_adicional_proveedor_orden
                
            
            cliente_iva_retenido = self.request.POST.get('cliente_iva_retenido')
            cliente_iva_trasladado = self.request.POST.get('cliente_iva_trasladado')
            cliente_subtotal_monto = self.request.POST.get('cliente_subtotal_monto')
            
            
            cliente_tipo_cambio = self.request.POST.get('cliente_tipo_cambio')
            proveedor_tipo_cambio = self.request.POST.get('proveedor_tipo_cambio')

            new_orden = Orden.objects.create(
                cliente_id=cliente_orden,
                costo_cliente=costo_cliente_orden,
                costo_adicional_cliente=adicional_cliente,
                wo=wo_orden,
                direccion_origen=direccion_origen,
                direccion_destino=direccion_destino,
                proveedor_id=proveedor_orden,
                costo_proveedor=costo_proveedor_orden,
                costo_adicional_proveedor=adicional_proveedor,
                eq_type=eq_type_orden,
                tipo_cambio=tipo_cambio_orden,
                pedimento=adicional_pedimento,
                pro=adicional_pro,
                load=adicional_load,
                mx_truck_num=adicional_mx_truck_num,
                us_truck_num=adicional_us_truck_num,
                mx_plate_num=adicional_mx_plate_num,
                us_plate_num=adicional_us_plate_num,
                realase=adicional_realase,
                mx_driver_one=adicional_mx_driver_one,
                mx_driver_two=adicional_mx_driver_two,
                vin=adicional_vin,
                lms=adicional_lms,
                us_driver_one=adicional_us_driver_one,
                invoice=adicional_invoice,
                mx_driver_phone_one=adicional_mx_driver_phone_one,
                us_driver_two=adicional_us_driver_two,
                empty_truck=adicional_empty_truck,
                us_driver_phone_one=adicional_us_driver_phone_one,
                cma=adicional_cma,
                maniobras=adicional_maniobras,
                estancias=adicional_estancias,
                otros=adicional_otros,
                loading_time=adicional_loading_time,
                waiting=adicional_waiting,
                crossing_time=adicional_crossing_time,
                serie=adicional_serie,
                folio=adicional_folio,
                uuid=adicional_uuid,
                status_orden_id=1,
                status_po_id=1,
                register_by=self.request.user.pk,
                # Campos para la parte de contabilidad
                cliente_factura=cliente_factura,
                cliente_cantidad=cliente_cantidad,
                factoraje_monto=factoraje_monto,
                saldo=saldo,
                monto_pago=monto_pago,
                pago_factoraje_referencia=pago_factoraje_referencia,
                pago_factoraje_monto=pago_factoraje_monto,
                proovedor_factura=proovedor_factura,
                proovedor_monto=proovedor_monto,
                proveedor_pago_monto=proveedor_pago_monto,
                esj_po=esj_po,
                flatbed=flatbed,
                carrier_mx=carrier_mx,
                carrier_usa=carrier_usa,
                created_at=fecha_orden
            )
            
            if cliente_tipo_cambio: 
                new_orden.cliente_tipo_cambio = cliente_tipo_cambio
            if proveedor_tipo_cambio:
                new_orden.proveedor_tipo_cambio = proveedor_tipo_cambio
            
            if cliente_iva_trasladado:
                new_orden.cliente_iva_trasladado = cliente_iva_trasladado
            if cliente_iva_retenido:
                new_orden.cliente_iva_retenido = cliente_iva_retenido
            if cliente_subtotal_monto:
                new_orden.cliente_subtotal_monto = cliente_subtotal_monto
            if adicional_load_type:
                new_orden.load_type = adicional_load_type
            if adicional_invoice_date:
                new_orden.invoice_date = adicional_invoice_date
            if adicional_notif_docs:
                new_orden.notif_docs = adicional_notif_docs
            if adicional_arrival:
                new_orden.arrival = adicional_arrival

            if cliente_factura_fecha:
                new_orden.cliente_factura_fecha = cliente_factura_fecha
            if cliente_pago_fecha:
                new_orden.cliente_pago_fecha = cliente_pago_fecha
            if factoraje_fecha_deposito:
                new_orden.factoraje_fecha_deposito = factoraje_fecha_deposito
            if fecha_pago:
                new_orden.fecha_pago = fecha_pago
            if pago_factoraje_fecha:
                new_orden.pago_factoraje_fecha = pago_factoraje_fecha
            if proveedor_pago_fecha:
                new_orden.proveedor_pago_fecha = proveedor_pago_fecha

            if loading_warehouse:
                new_orden.loading_warehouse = datetime.strptime(loading_warehouse.replace('T', ' '), '%Y-%m-%d %H:%M')
            if departure_esj:
                new_orden.departure_esj = datetime.strptime(departure_esj.replace('T', ' '), '%Y-%m-%d %H:%M')
            if arrival_juarez:
                new_orden.arrival_juarez = datetime.strptime(arrival_juarez.replace('T', ' '), '%Y-%m-%d %H:%M')
            if arrival_el_paso:
                new_orden.arrival_el_paso = datetime.strptime(arrival_el_paso.replace('T', ' '), '%Y-%m-%d %H:%M')
            if departure_usa:
                new_orden.departure_usa = datetime.strptime(departure_usa.replace('T', ' '), '%Y-%m-%d %H:%M')
            if arrival_destination:
                new_orden.arrival_destination = datetime.strptime(arrival_destination.replace('T', ' '),
                                                                  '%Y-%m-%d %H:%M')
            new_orden.save()

            # Hacemos un parse de la variable points para recorrerla
            list_point = json.loads(points)
            for point in list_point:
                new_point = Orden_Shipper_Delivery.objects.create(
                    orden=new_orden,
                    producto_id=point['producto']['id'],
                    tipo=point['tipo_point']['id'],
                    qty=point['qty_point'],
                    weight=point['weight_point'],
                    # precio=point['precio_point'],
                    po_numbers=point['po_numbers_point'],
                )
                for shipper in point['shipper_point']:
                    new_shipper = ShipperDeliveryPoints.objects.create(
                        tipo=1,
                        date=point['date_shipper_point'],
                        notes=point['shipping_notes_point'],
                        shipper_delivery_id=shipper['id'],
                        order_shipper_delivery=new_point

                    )
                for delivery in point['delivery_point']:
                    new_delivery = ShipperDeliveryPoints.objects.create(
                        tipo=2,
                        date=point['date_delivery_point'],
                        notes=point['delivery_notes_point'],
                        shipper_delivery_id=delivery['id'],
                        order_shipper_delivery=new_point
                    )

            tracking_log = TrackingLogOrden.objects.create(
                orden_id=new_orden.pk,
                status_orden_id=new_orden.status_orden.pk,
                register_by=self.request.user.pk
            )

            tracking_log = TrackingLogOrden.objects.create(
                orden_id=new_orden.pk,
                status_po_id=new_orden.status_po.pk,
                register_by=self.request.user.pk
            )
            return JsonResponse({'message': 'Orden creada exitosamente'}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar crear la orden'}, status=400)


class OrdenEditTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'ordenes/orden_add_edit.html'

    def get_context_data(self, **kwargs):
        context = super(OrdenEditTemplateView, self).get_context_data(**kwargs)
        context['orden'] = Orden.objects.get(pk=self.kwargs.get('orden'))
        context['clientes'] = Cliente.objects.all().exclude(activo=False)
        context['proveedores'] = Proveedor.objects.all().exclude(activo=False)
        context['productos'] = Producto.objects.all().exclude(activo=False)
        context['shippers'] = Shipper_Delivery.objects.all().exclude(tipo=2)
        context['deliverys'] = Shipper_Delivery.objects.all().exclude(tipo=1)
        context['edicion'] = True
        context['forloop'] = self.request.GET.get('forloop')
        shipper_delivery_points = []
        points = Orden_Shipper_Delivery.objects.filter(orden=Orden.objects.get(pk=self.kwargs.get('orden')))
        iteracion = 0
        for point in points:
            date_shipp = ''
            date_delivery = ''
            note_shipp = ''
            note_delivery = ''
            shipper = []
            delivery = []
            shipp_delivery = ShipperDeliveryPoints.objects.filter(order_shipper_delivery=point.pk)
            for ship_del in shipp_delivery:
                if ship_del.tipo == 1:
                    shipper.append({
                        "id": "{}".format(ship_del.shipper_delivery.id),
                        "nombre": "{}".format(ship_del.shipper_delivery.nombre)
                    })
                    date_shipp = str(ship_del.date)
                    note_shipp = str(ship_del.notes)
                else:
                    delivery.append({
                        "id": "{}".format(ship_del.shipper_delivery.id),
                        "nombre": "{}".format(ship_del.shipper_delivery.nombre)
                    })
                    date_delivery = str(ship_del.date)
                    note_delivery = str(ship_del.notes)
            shipper_delivery_points.append({
                "id": iteracion + 1,
                "producto": {
                    "id": point.producto.id,
                    "nombre": point.producto.nombre
                },
                "tipo_point": {
                    "id": point.tipo,
                    "nombre": point.get_tipo_display()
                },
                "qty_point": point.qty,
                "weight_point": point.weight,
                "po_numbers_point": point.po_numbers,
                "shipper_point": shipper,
                "date_shipper_point": date_shipp,
                "shipping_notes_point": note_shipp,
                "delivery_point": delivery,
                "date_delivery_point": date_delivery,
                "delivery_notes_point": note_delivery
            })
        context["points"] = shipper_delivery_points
        return context

    @transaction.atomic()
    def post(self, request, **kwargs):
        try:
            idOrden = self.kwargs.get('orden')
            orden = Orden.objects.get(pk=idOrden)
            # Obtenemos los datos enviados a traves de la petición AJAX
            points = self.request.POST.get('points')
            cliente_orden = self.request.POST.get('cliente_orden')
            costo_cliente_orden = self.request.POST.get('costo_cliente_orden')
            costo_adicional_cliente_orden = self.request.POST.get('costo_adicional_cliente_orden')
            wo_orden = self.request.POST.get('wo_orden')
            direccion_origen = self.request.POST.get('direccion_origen')
            direccion_destino = self.request.POST.get('direccion_destino')
            proveedor_orden = self.request.POST.get('proveedor_orden')
            costo_proveedor_orden = self.request.POST.get('costo_proveedor_orden')
            costo_adicional_proveedor_orden = self.request.POST.get('costo_adicional_proveedor_orden')
            eq_type_orden = self.request.POST.get('eq_type_orden')
            tipo_cambio_orden = self.request.POST.get('tipo_cambio_orden')
            adicional_pedimento = self.request.POST.get('adicional_pedimento')
            adicional_pro = self.request.POST.get('adicional_pro')
            adicional_load = self.request.POST.get('adicional_load')
            adicional_mx_truck_num = self.request.POST.get('adicional_mx_truck_num')
            adicional_us_truck_num = self.request.POST.get('adicional_us_truck_num')
            adicional_load_type = self.request.POST.get('adicional_load_type')
            adicional_mx_plate_num = self.request.POST.get('adicional_mx_plate_num')
            adicional_us_plate_num = self.request.POST.get('adicional_us_plate_num')
            adicional_realase = self.request.POST.get('adicional_realase')
            adicional_mx_driver_one = self.request.POST.get('adicional_mx_driver_one')
            adicional_mx_driver_two = self.request.POST.get('adicional_mx_driver_two')
            adicional_vin = self.request.POST.get('adicional_vin')
            adicional_lms = self.request.POST.get('adicional_lms')
            adicional_us_driver_one = self.request.POST.get('adicional_us_driver_one')
            adicional_invoice = self.request.POST.get('adicional_invoice')
            adicional_mx_driver_phone_one = self.request.POST.get('adicional_mx_driver_phone_one')
            adicional_us_driver_two = self.request.POST.get('adicional_us_driver_two')
            adicional_invoice_date = self.request.POST.get('adicional_invoice_date')
            adicional_empty_truck = self.request.POST.get('adicional_empty_truck')
            adicional_us_driver_phone_one = self.request.POST.get('adicional_us_driver_phone_one')
            adicional_notif_docs = self.request.POST.get('adicional_notif_docs')
            adicional_cma = self.request.POST.get('adicional_cma')
            adicional_maniobras = self.request.POST.get('adicional_maniobras')
            adicional_estancias = self.request.POST.get('adicional_estancias')
            adicional_otros = self.request.POST.get('adicional_otros')
            adicional_arrival = self.request.POST.get('adicional_arrival')
            adicional_loading_time = self.request.POST.get('adicional_loading_time')
            adicional_waiting = self.request.POST.get('adicional_waiting')
            adicional_crossing_time = self.request.POST.get('adicional_crossing_time')
            adicional_serie = self.request.POST.get('adicional_serie')
            adicional_folio = self.request.POST.get('adicional_folio')
            adicional_uuid = self.request.POST.get('adicional_uuid')
            # Campos para la nueva parte de contabilidad
            cliente_factura = self.request.POST.get('cliente_factura')
            cliente_factura_fecha = self.request.POST.get('cliente_factura_fecha')
            cliente_pago_fecha = self.request.POST.get('cliente_pago_fecha')
            cliente_cantidad = self.request.POST.get('cliente_cantidad')
            factoraje_fecha_deposito = self.request.POST.get('factoraje_fecha_deposito')
            factoraje_monto = self.request.POST.get('factoraje_monto')
            saldo = self.request.POST.get('saldo')
            fecha_pago = self.request.POST.get('fecha_pago')
            monto_pago = self.request.POST.get('monto_pago')
            pago_factoraje_fecha = self.request.POST.get('pago_factoraje_fecha')
            pago_factoraje_referencia = self.request.POST.get('pago_factoraje_referencia')
            pago_factoraje_monto = self.request.POST.get('pago_factoraje_monto')
            proovedor_factura = self.request.POST.get('proovedor_factura')
            proovedor_monto = self.request.POST.get('proovedor_monto')
            proveedor_pago_fecha = self.request.POST.get('proveedor_pago_fecha')
            proveedor_pago_monto = self.request.POST.get('proveedor_pago_monto')

            esj_po = self.request.POST.get('esj_po')
            flatbed = self.request.POST.get('flatbed')
            carrier_mx = self.request.POST.get('carrier_mx')
            carrier_usa = self.request.POST.get('carrier_usa')
            loading_warehouse = self.request.POST.get('loading_warehouse')
            departure_esj = self.request.POST.get('departure_esj')
            arrival_juarez = self.request.POST.get('arrival_juarez')
            arrival_el_paso = self.request.POST.get('arrival_el_paso')
            departure_usa = self.request.POST.get('departure_usa')
            arrival_destination = self.request.POST.get('arrival_destination')
            fecha_orden = self.request.POST.get('fecha_orden')
            
            cliente_iva_retenido = self.request.POST.get('cliente_iva_retenido')
            cliente_iva_trasladado = self.request.POST.get('cliente_iva_trasladado')
            cliente_subtotal_monto = self.request.POST.get('cliente_subtotal_monto')

            cliente_tipo_cambio = self.request.POST.get('cliente_tipo_cambio')
            proveedor_tipo_cambio = self.request.POST.get('proveedor_tipo_cambio')
            
            # Reamplazaremos todos los datos de la orden
            orden.cliente_id = cliente_orden
            orden.costo_cliente = costo_cliente_orden
            orden.costo_adicional_cliente = costo_adicional_cliente_orden
            orden.wo = wo_orden
            orden.direccion_origen = direccion_origen
            orden.direccion_destino = direccion_destino
            orden.proveedor_id = proveedor_orden
            orden.costo_proveedor = costo_proveedor_orden
            orden.costo_adicional_proveedor = costo_adicional_proveedor_orden
            orden.eq_type = eq_type_orden
            orden.tipo_cambio = tipo_cambio_orden
            orden.pedimento = adicional_pedimento
            orden.pro = adicional_pro
            orden.load = adicional_load
            orden.mx_truck_num = adicional_mx_truck_num
            orden.us_truck_num = adicional_us_truck_num
            orden.mx_plate_num = adicional_mx_plate_num
            orden.us_plate_num = adicional_us_plate_num
            orden.realase = adicional_realase
            orden.mx_driver_one = adicional_mx_driver_one
            orden.mx_driver_two = adicional_mx_driver_two
            orden.vin = adicional_vin
            orden.lms = adicional_lms
            orden.us_driver_one = adicional_us_driver_one
            orden.invoice = adicional_invoice
            orden.mx_driver_phone_one = adicional_mx_driver_phone_one
            orden.us_driver_two = adicional_us_driver_two
            orden.empty_truck = adicional_empty_truck
            orden.us_driver_phone_one = adicional_us_driver_phone_one
            orden.cma = adicional_cma
            orden.maniobras = adicional_maniobras
            orden.estancias = adicional_estancias
            orden.otros = adicional_otros
            orden.loading_time = adicional_loading_time
            orden.waiting = adicional_waiting
            orden.crossing_time = adicional_crossing_time
            orden.serie = adicional_serie
            orden.folio = adicional_folio
            orden.uuid = adicional_uuid
            orden.esj_po = esj_po
            orden.flatbed = flatbed
            orden.carrier_mx = carrier_mx
            orden.carrier_usa = carrier_usa
            # Campos para la parte de contabilidad
            orden.cliente_factura = cliente_factura
            orden.cliente_cantidad = cliente_cantidad
            orden.factoraje_monto = factoraje_monto
            orden.saldo = saldo
            orden.monto_pago = monto_pago
            orden.pago_factoraje_referencia = pago_factoraje_referencia
            orden.pago_factoraje_monto = pago_factoraje_monto
            orden.proovedor_factura = proovedor_factura
            orden.proovedor_monto = proovedor_monto
            orden.proveedor_pago_monto = proveedor_pago_monto
            orden.created_at = fecha_orden
            if cliente_tipo_cambio: 
                orden.cliente_tipo_cambio = cliente_tipo_cambio
            if proveedor_tipo_cambio:
                orden.proveedor_tipo_cambio = proveedor_tipo_cambio

            if cliente_iva_trasladado:
                orden.cliente_iva_trasladado = cliente_iva_trasladado
            if cliente_iva_retenido:
                orden.cliente_iva_retenido = cliente_iva_retenido
            if cliente_subtotal_monto:
                orden.cliente_subtotal_monto = cliente_subtotal_monto
            
            if adicional_load_type:
                orden.load_type = adicional_load_type
            if adicional_invoice_date:
                orden.invoice_date = adicional_invoice_date
            if adicional_notif_docs:
                orden.notif_docs = adicional_notif_docs
            if adicional_arrival:
                orden.arrival = adicional_arrival

            if cliente_factura_fecha:
                orden.cliente_factura_fecha = cliente_factura_fecha
            if cliente_pago_fecha:
                orden.cliente_pago_fecha = cliente_pago_fecha
            if factoraje_fecha_deposito:
                orden.factoraje_fecha_deposito = factoraje_fecha_deposito
            if fecha_pago:
                orden.fecha_pago = fecha_pago
            if pago_factoraje_fecha:
                orden.pago_factoraje_fecha = pago_factoraje_fecha
            if proveedor_pago_fecha:
                orden.proveedor_pago_fecha = proveedor_pago_fecha

            if loading_warehouse:
                orden.loading_warehouse = datetime.strptime(loading_warehouse.replace('T', ' '), '%Y-%m-%d %H:%M')
            if departure_esj:
                orden.departure_esj = datetime.strptime(departure_esj.replace('T', ' '), '%Y-%m-%d %H:%M')
            if arrival_juarez:
                orden.arrival_juarez = datetime.strptime(arrival_juarez.replace('T', ' '), '%Y-%m-%d %H:%M')
            if arrival_el_paso:
                orden.arrival_el_paso = datetime.strptime(arrival_el_paso.replace('T', ' '), '%Y-%m-%d %H:%M')
            if departure_usa:
                orden.departure_usa = datetime.strptime(departure_usa.replace('T', ' '), '%Y-%m-%d %H:%M')
            if arrival_destination:
                orden.arrival_destination = datetime.strptime(arrival_destination.replace('T', ' '), '%Y-%m-%d %H:%M')
            orden.save()
            # Buscamos todos los puntos existentes y los borramos para crear los nuevos
            points_old = Orden_Shipper_Delivery.objects.filter(orden=orden)
            shipper_delivery_old = ShipperDeliveryPoints.objects.filter(
                order_shipper_delivery_id__in=points_old.values_list('pk'))
            shipper_delivery_old.delete()
            points_old.delete()
            # Hacemos un parse de la variable points para recorrerla
            list_point = json.loads(points)
            for point in list_point:
                new_point = Orden_Shipper_Delivery.objects.create(
                    orden=orden,
                    producto_id=point['producto']['id'],
                    tipo=point['tipo_point']['id'],
                    qty=point['qty_point'],
                    weight=point['weight_point'],
                    # precio=point['precio_point'],
                    po_numbers=point['po_numbers_point'],
                )
                for shipper in point['shipper_point']:
                    new_shipper = ShipperDeliveryPoints.objects.create(
                        tipo=1,
                        date=point['date_shipper_point'],
                        notes=point['shipping_notes_point'],
                        shipper_delivery_id=shipper['id'],
                        order_shipper_delivery=new_point

                    )
                for delivery in point['delivery_point']:
                    new_delivery = ShipperDeliveryPoints.objects.create(
                        tipo=2,
                        date=point['date_delivery_point'],
                        notes=point['delivery_notes_point'],
                        shipper_delivery_id=delivery['id'],
                        order_shipper_delivery=new_point
                    )
            return JsonResponse({'message': 'Orden actualizada exitosamente exitosamente'}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar actualizar la orden'}, status=400)


class OrdenDeleteApiView(LoginRequiredMixin, APIView):

    def post(self, request):
        try:
            idOrden = self.request.POST.get('orden')
            orden = Orden.objects.get(pk=idOrden)
            # Obtenemos todos los points de la orden y los eliminamos
            points = Orden_Shipper_Delivery.objects.filter(orden=orden)
            points.delete()
            orden.delete()
            return JsonResponse({'message': 'Orden eliminada '}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar crear la orden'}, status=400)


class UsuariosListTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'usuarios/usuarios_list.html'

    def get_context_data(self, **kwargs):
        context = super(UsuariosListTemplateView, self).get_context_data(**kwargs)
        context['usuarios'] = PersonaSistema.objects.filter(activo=True)
        context['clientes'] = Cliente.objects.all()
        return context


class NewUsuarioApiView(LoginRequiredMixin, APIView):

    @transaction.atomic()
    def post(self, request):
        try:
            # Recibimos los parametros mediante la petición ajax
            nombre = self.request.POST.get('nombre')
            ap_paterno = self.request.POST.get('ap_paterno')
            ap_materno = self.request.POST.get('ap_materno')
            email = self.request.POST.get('correo_electronico')
            tipo_usuario = self.request.POST.get('tipo_usuario')
            username = self.request.POST.get('username')
            password = self.request.POST.get('contrasenia')
            # Validaremos que no exista el mismo correo para usuarios ya creados
            if not PersonaSistema.objects.filter(correo=email, activo=True).exists():
                # Procedemos a validar el username
                if not PersonaSistema.objects.filter(usuario__username=username, activo=True).exists():
                    new_person = PersonaSistema.objects.create(
                        nombre=nombre,
                        ap_paterno=ap_paterno,
                        ap_materno=ap_materno,
                        correo=email,
                        register_by=self.request.user.pk
                    )
                    new_user = User.objects.create(
                        username=username,
                        first_name=nombre,
                        last_name=ap_paterno,
                        email=email
                    )
                    new_user.set_password(password)
                    if tipo_usuario == '1':
                        new_user.administrador = True
                    if tipo_usuario == '2':
                        new_user.ejecutivo = True
                    if tipo_usuario == '3':
                        new_user.cliente = True
                        new_person.cliente_id = self.request.POST.get('cliente_id')
                    new_user.save()
                    new_person.usuario = new_user
                    new_person.save()
                    from_address = settings.EMAIL_HOST_USER
                    to_address = email
                    password_address = settings.EMAIL_HOST_PASSWORD
                    msg = MIMEMultipart('alternative')
                    msg['To'] = from_address
                    msg['Subject'] = 'SILOGISTICS TRANSPORT - CREDENCIALES DE ACCESO'
                    msg['From'] = to_address
                    plantilla = f'''
                                <div>
                                    <div
                                        style="width: 100%; text-align: center; padding-top: 10px; padding-bottom: 5px; border-bottom: 15px solid #00026b;">
                                        <img src="https://ctrl.si-go.com/misc/silogo_w.png">
                                    </div>
                                    <div>
                                        <p style="text-align: justify; font-size: 15px; font-weight: lighter;">
                                            La empresa <b>SILOGISTICS</b> en un esfuerzo de hacer eficiente nuestras tareas diarias con el uso innovador
                                            de las nuevas Tecnologías de la Información, es un gusto darle la bienvenida a nuestra nueva <b>Aplicación
                                                WEB</b>,
                                            que nos permite agilizar y digitalizar las diversas actividades de la Institución para mejorar la eficiencia
                                            de los procesos de gestión documental, reducir el espacio físico dedicado al archivo de documentos y
                                            facilita el acceso a la información.
                                        <p style="margin-top: 10px; text-indent: 40px; font-size: 15px">
                                            A través de este medio le hacemos la entrega de su usuario, contraseña y le
                                            compartimos la dirección electrónica para poder ingresar a la Aplicación WEB.
                                        </p>
                                        <p style="margin-top: 20px"><b>Bienvenido/a: {new_person.nombre} {new_person.ap_paterno}</b></p>
                                        <div
                                            style="background-color: #00026b;  color:white; font-size: 25px; text-align: center; padding-top: 10px; padding-bottom: 10px;">
                                            <b>SILOGISTICS WEB</b>
                                        </div>
                                        <div style="text-align: center; margin-top: 5px; line-height: 30px">
                                            <p style="font-size: 15px"><b>URL de la paltaforma: <a href="{settings.IP_SERVER}login/"
                                                        target="_blank">{settings.IP_SERVER}login/</a></b> <br>
                                                <b>{new_person.nombre} {new_person.ap_paterno}</b> <br>
                                                <b>Usuario:</b> {new_user.username} <br>
                                                <b>Contraseña:</b> {password} <br>
                                                <b>Sin mas por el momento deseo que tenga buen dia.</b>
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                '''
                    message = MIMEText(plantilla, 'html')
                    msg.attach(message)
                    smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.login(from_address, password_address)
                    smtp.sendmail(from_address, to_address, msg.as_string())
                    smtp.quit()
                    return JsonResponse({'message': 'Usuario creado exitosamente '}, status=200)
                else:
                    return JsonResponse({'message': 'Ya existe un registro con ese nombre de usuario '}, status=400)
            else:
                return JsonResponse({'message': 'Ya existe un usuario registrado con ese email'}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar crear el usuario', 'e': e}, status=400)


class DeleteUsuarioApiVieW(LoginRequiredMixin, APIView):

    def post(self, request):
        try:
            idPersona = self.request.POST.get('persona')
            persona = PersonaSistema.objects.get(pk=idPersona)
            persona.usuario.delete()
            persona.delete()
            return JsonResponse({'message': 'Usuario Eliminado Exitosamente'}, status=200)
        except Exception as e:
            return JsonResponse({'message': 'Hubo un error al intentar eliminar el usuario'}, status=400)


class OrdenTrackingLogApiView(LoginRequiredMixin, APIView):

    def get(self, request):
        try:
            if not self.request.GET.get('status'):
                print('Embarque')
                tracking_logs = TrackingLogOrden.objects.filter(orden_id=self.request.GET.get('orden_id'),
                                                                status_orden__isnull=False).order_by('-pk')
            else:
                print('PO')
                tracking_logs = TrackingLogOrden.objects.filter(orden_id=self.request.GET.get('orden_id'),
                                                                status_po__isnull=False).order_by('-pk')

            serializers = TrackingLogSerializers(tracking_logs, many=True)
            return JsonResponse({'tracking': serializers.data}, status=200)
        except Exception as e:
            return JsonResponse({'message': 'Hubo un error al intentar consultar el tracking log de la orden'},
                                status=400)

    @transaction.atomic()
    def post(self, request):
        try:
            orden = Orden.objects.get(pk=self.request.POST.get('orden_id'))
            if self.request.POST.get('type_status') == 'orden':
                tracking_log = TrackingLogOrden.objects.create(
                    orden_id=self.request.POST.get('orden_id'),
                    status_orden_id=self.request.POST.get('status'),
                    nota=self.request.POST.get('descripcion'),
                    register_by=self.request.user.pk
                )
                orden.status_orden_id = self.request.POST.get('status')
            else:
                tracking_log = TrackingLogOrden.objects.create(
                    orden_id=self.request.POST.get('orden_id'),
                    status_po_id=self.request.POST.get('status'),
                    nota=self.request.POST.get('descripcion'),
                    register_by=self.request.user.pk
                )
                orden.status_po_id = self.request.POST.get('status')
            orden.save()
            return JsonResponse({'message': 'Tracking Log registrado exitosamente'}, status=200)
        except Exception as e:
            return JsonResponse({'message': 'Hubo un error al intentar agregar el Tracking Log'}, status=400)


#################### Procesos para la vistas de los reportes ####################

class ReporteFiltroFechas(LoginRequiredMixin, APIView):

    def get(self, request):
        try:
            query = "select get_ordenes_all_tarifa(null,null)"
            startDate = self.request.GET.get('startDate')
            if startDate and self.request.GET.get('endDate'):
                endDate = datetime.strptime(self.request.GET.get('endDate'), "%Y-%m-%d") + timedelta(days=1)
                query = "select get_ordenes_all_tarifa('{}','{}')".format(startDate,endDate)
            elif startDate:
                query = "select get_ordenes_all_tarifa('{}',null)".format(startDate)
            elif self.request.GET.get('endDate'):
                endDate = datetime.strptime(self.request.GET.get('endDate'), "%Y-%m-%d") + timedelta(days=1)
                query = "select get_ordenes_all_tarifa(null,'{}')".format(endDate)
            conection = connection.cursor()
            conection.execute(query)
            query_success = dictfetchall(conection)
            print(query_success)
            return JsonResponse({'ordenes': query_success[0]['get_ordenes_all_tarifa']}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar realizar la busqueda'},
                                status=400)


class ReporteFiltroCiudades(APIView):
    def get(self, request):
        try:
            exitAddress = self.request.GET.get('exitAddress')
            destinationAddress = self.request.GET.get('destinationAddress')
            eqType = self.request.GET.get('eqType')
            # Obtenemos las shippers o deliverys de la ciudad
            # Haremos el proceso para obtener las ordenes con shipper o delivery de esa ciudad
            listOrdenesEncontradas 
            listOrdenes = Orden.objects.all().order_by('-pk')
            if eqType:
                if eqType == '1':
                    listOrdenes = listOrdenes.filter(eq_type=eqType)
                if eqType == '2':
                    listOrdenes = listOrdenes.filter(Q(eq_type=2) | Q(eq_type=4))
                if eqType == '3':
                    listOrdenes = listOrdenes.filter(Q(eq_type=3) | Q(eq_type=5))

            listOrdenesEncontradas = []
            for orden in listOrdenes:
                print(orden)
                if exitAddress and destinationAddress:
                    points = Orden_Shipper_Delivery.objects.filter(orden_id=orden.pk).values_list('pk')
                    originDestino = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points)
                    if originDestino:
                        if originDestino[0].shipper_delivery.cuidad.pk == int(exitAddress) and originDestino[
                            1].shipper_delivery.cuidad.pk == int(destinationAddress):
                            jsonData = {
                                "id": originDestino[0].order_shipper_delivery.orden.pk,
                                # "origen": originDestino[0].order_shipper_delivery.orden.get_origin(),
                                # "destino": originDestino[0].order_shipper_delivery.orden.get_destination(),
                                "cliente": originDestino[0].order_shipper_delivery.orden.cliente.nombre,
                                "proveedor": originDestino[0].order_shipper_delivery.orden.proveedor.nombre,
                                "eq_type": originDestino[0].order_shipper_delivery.orden.get_eq_type_display(),
                                "costo_cliente": originDestino[0].order_shipper_delivery.orden.costo_cliente,
                                "costo_adicional_cliente": originDestino[
                                    0].order_shipper_delivery.orden.costo_adicional_cliente,
                                "costo_proveedor": originDestino[0].order_shipper_delivery.orden.costo_proveedor,
                                "costo_adicional_proveedor": originDestino[
                                    0].order_shipper_delivery.orden.costo_adicional_proveedor,
                                "utilidad": originDestino[0].order_shipper_delivery.orden.get_utilidad(),
                                "created_at": originDestino[0].order_shipper_delivery.orden.created_at
                            }
                            listOrdenesEncontradas.append(jsonData)
                elif exitAddress:
                    points = Orden_Shipper_Delivery.objects.filter(orden_id=orden.pk).values_list('pk')
                    origin = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points,
                                                                  tipo=1, ).order_by(
                        'pk')
                    if origin:
                        if origin[0].shipper_delivery.cuidad.pk == int(exitAddress):
                            jsonData = {
                                "id": origin[0].order_shipper_delivery.orden.pk,
                                "cliente": origin[0].order_shipper_delivery.orden.cliente.nombre,
                                "proveedor": origin[0].order_shipper_delivery.orden.proveedor.nombre,
                                "eq_type": origin[0].order_shipper_delivery.orden.get_eq_type_display(),
                                "costo_cliente": origin[0].order_shipper_delivery.orden.costo_cliente,
                                "costo_adicional_cliente": origin[
                                    0].order_shipper_delivery.orden.costo_adicional_cliente,
                                "costo_proveedor": origin[0].order_shipper_delivery.orden.costo_proveedor,
                                "costo_adicional_proveedor": origin[
                                    0].order_shipper_delivery.orden.costo_adicional_proveedor,
                                "utilidad": origin[0].order_shipper_delivery.orden.get_utilidad(),
                                "created_at": origin[0].order_shipper_delivery.orden.created_at
                            }
                            listOrdenesEncontradas.append(jsonData)
                elif destinationAddress:
                    points = Orden_Shipper_Delivery.objects.filter(orden_id=orden.pk).values_list('pk')
                    destination = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points,
                                                                       tipo=2).order_by('pk')
                    if destination:
                        if destination[0].shipper_delivery.cuidad.pk == int(destinationAddress):
                            jsonData = {
                                "id": destination[0].order_shipper_delivery.orden.pk,
                                "cliente": destination[0].order_shipper_delivery.orden.cliente.nombre,
                                "proveedor": destination[0].order_shipper_delivery.orden.proveedor.nombre,
                                "eq_type": destination[0].order_shipper_delivery.orden.get_eq_type_display(),
                                "costo_cliente": destination[0].order_shipper_delivery.orden.costo_cliente,
                                "costo_adicional_cliente": destination[
                                    0].order_shipper_delivery.orden.costo_adicional_cliente,
                                "costo_proveedor": destination[0].order_shipper_delivery.orden.costo_proveedor,
                                "costo_adicional_proveedor": destination[
                                    0].order_shipper_delivery.orden.costo_adicional_proveedor,
                                "utilidad": destination[0].order_shipper_delivery.orden.get_utilidad(),
                                "created_at": destination[0].order_shipper_delivery.orden.created_at
                            }
                            listOrdenesEncontradas.append(jsonData)
                else:
                    jsonData = {
                        "id": orden.pk,
                        "cliente": orden.cliente.nombre,
                        "proveedor": orden.proveedor.nombre,
                        "eq_type": orden.get_eq_type_display(),
                        "costo_cliente": orden.costo_cliente,
                        "costo_adicional_cliente": orden.costo_adicional_cliente,
                        "costo_proveedor": orden.costo_proveedor,
                        "costo_adicional_proveedor": orden.costo_adicional_proveedor,
                        "utilidad": orden.get_utilidad(),
                        "created_at": orden.created_at
                    }
                    listOrdenesEncontradas.append(jsonData)
            return JsonResponse({'ordenes': listOrdenesEncontradas}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar realizar la busqueda'},
                                status=400)


class ReporteContabilidad(TemplateView):
    template_name = 'reportes/reporte_contabilidad.html'

    def get_context_data(self, **kwargs):
        context = super(ReporteContabilidad, self).get_context_data(**kwargs)
        conection = connection.cursor()
        query = "select get_ordenes_all_tarifa(null,null)"
        conection.execute(query)
        query_success = dictfetchall(conection)
        print(query_success)
        # listOrdenes = Orden.objects.all().exclude(status_po_id=17).order_by('-pk')
        context['ordenes'] = query_success[0]['get_ordenes_all_tarifa']
        return context


class ReporteRutas(TemplateView):
    template_name = 'reportes/reportes_rutas.html'

    def get_context_data(self, **kwargs):
        context = super(ReporteRutas, self).get_context_data(**kwargs)
        conection = connection.cursor()
        query = "select ciudades_all()"
        conection.execute(query)
        query_success = dictfetchall(conection)
        print(query_success)
        context['ciudades'] = query_success[0]['ciudades_all']
        return context


#################### Procesos para la vistas de la creación de los reportes por usuarios ####################


class ReporteClienteListado(TemplateView):
    template_name = 'reporte_clientes/reporte_clientes_list.html'

    def get_context_data(self, **kwargs):
        context = super(ReporteClienteListado, self).get_context_data(**kwargs)
        context['reportes'] = FormatoCliente.objects.all()
        return context


class ReporteClienteAdd(TemplateView):
    template_name = 'reporte_clientes/reporte_clientes_add_edit.html'

    def get_context_data(self, **kwargs):
        context = super(ReporteClienteAdd, self).get_context_data(**kwargs)
        context['clientes'] = Cliente.objects.all().exclude(activo=False).order_by('nombre')
        context['camposDisponibles'] = CamposDisponiblesSistema.objects.all()
        return context

    @transaction.atomic()
    def post(self, request):
        try:
            arrCamposSelected = self.request.POST.get('camposDisponibles')
            nombreReporte = self.request.POST.get('nombre_reporte')
            clienteIDReporte = self.request.POST.get('cliente_reporte')
            if not FormatoCliente.objects.filter(nombre=nombreReporte.upper(), cliente__id=clienteIDReporte).exists():
                new_formato = FormatoCliente.objects.create(
                    nombre=nombreReporte.upper(),
                    cliente_id=clienteIDReporte,
                    register_by=self.request.user.pk
                )
                for campo in json.loads(arrCamposSelected):
                    print(campo['idCampo'])
                    new_campo_formato = CamposFormatosClientes.objects.create(
                        formato=new_formato,
                        campo_id=campo['idCampo']
                    )
                return JsonResponse({'message': 'Reporte Creado Exitosamente'},
                                    status=200)
            else:
                return JsonResponse({'message': 'Ya hay un reporte creado con ese nombre para el cliente seleccionado'},
                                    status=400)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar guardar el reporte'},
                                status=400)


class ReporteClienteDelete(APIView):

    def post(self, request):
        try:
            idReporte = self.request.POST.get('reporteID')
            reporte = FormatoCliente.objects.get(pk=idReporte)
            camposReporte = CamposFormatosClientes.objects.filter(formato_id=idReporte)
            camposReporte.delete()
            reporte.delete()
            return JsonResponse({'message': 'Reporte eliminado Exitosamente'},
                                status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Hubo un error al intentar eliminar el reporte'},
                                status=400)


class ReportesGeneradosCliente(APIView):

    def get(self, request):
        idUser = self.request.user.pk
        objPersona = PersonaSistema.objects.get(usuario_id=idUser)
        arrFormatos = FormatoCliente.objects.filter(cliente_id=objPersona.cliente.id)
        serializersFormatos = ReporteOrdenesClienteSerializers(arrFormatos, many=True)
        return JsonResponse({"reportes": serializersFormatos.data}, status=200)


class UtilidadOrdenes(TemplateView):
    
    template_name='utilidad.html'
    
    def get_context_data(self, **kwargs):
        context = super(UtilidadOrdenes, self).get_context_data(**kwargs)
        # context['noSemanas'] = 52
        if not self.request.GET.get('semana'):
            # Si no viene el filtro de semana buscaremos mediante la semana actual
            today = datetime.now()
            inicio_semana = today
            arrInformacion = []
            context['semanaSelected'] = today.today().isocalendar()[1]
            # Restaremos los dias a la fecha actual para llegar al inicio de la semana (lunes)
            if int(datetime.now().strftime("%W")) == 0:
                inicio_semana = today - timedelta(days=6)
            else:
                dias_diferencia = int(datetime.now().strftime("%w")) - 1
                if dias_diferencia >= 1:
                    inicio_semana = today - timedelta(days=dias_diferencia)
        else:
            semanaSelected = self.request.GET.get('semana')
            year = 2023
            # Al encontrar el inicio de la semana siempre empezara en "lunes" por lo tanto tenemos que restart un dia para iniciar la semana de lun-dom.
            diasSemana = datetime.strptime(f'{year}-W{int(semanaSelected)}-1', '%Y-W%W-%w')
            inicio_semana = diasSemana
            context['semanaSelected'] = int(semanaSelected)
        arrInformacion = []
        ventaSemanal = 0
        compraSemanal = 0
        utilidadSemanal = 0
        margenSemanal = 0
        for x in range(0, 7):
            dia_semana = inicio_semana + timedelta(days=x)
            # Haremos el proceso para encontrar todas las ordenes del dia tomando en cuenta las operaciones que se tienen que hacer
            ordenes = Orden.objects.filter(created_at__day=dia_semana.strftime('%d'),
                                            created_at__month=dia_semana.strftime('%m'),
                                            created_at__year=dia_semana.strftime('%Y'))
            venta = 0
            compra = 0
            if not ordenes:
                arrInformacion.append({
                    "dia_semana": dia_semana,
                    "venta": 0,
                    "compra": 0,
                    "utilidad": 0,
                    "margen": 0,
                })
            else:
                # Recorremos las ordenes para ir sumando las compras y ventas del dia
                for orden in ordenes:
                    venta += int(orden.costo_cliente) + int(orden.costo_adicional_cliente)
                    compra += int(orden.costo_proveedor) + int(orden.costo_adicional_proveedor)
                if venta == 0 or (venta - compra) == 0:
                    arrInformacion.append({
                        "dia_semana": dia_semana,
                        "venta": venta,
                        "compra": compra,
                        "utilidad": venta - compra,
                        "margen": 0
                    })
                else:
                    arrInformacion.append({
                        "dia_semana": dia_semana,
                        "venta": venta,
                        "compra": compra,
                        "utilidad": venta - compra,
                        "margen": ((venta - compra) / venta) * 100
                    })
                ventaSemanal += venta
                compraSemanal += compra
                utilidadSemanal +=  (venta - compra)
                     
            context['ordenes_dias'] = arrInformacion

            # Proceso para obtener los clientes del sistema
            arrInformacionCustomer = []
            arrClientes = Cliente.objects.all().exclude(activo=False).order_by('nombre')
            for cliente in arrClientes:
                ventaSemanalCustomer = 0
                compraSemanalCustomer = 0
                utilidadSemanalCustomer = 0
                arrSemanaCustomer = []
                for x in range(0, 7):
                    dia_semana = inicio_semana + timedelta(days=x)
                    # Haremos el proceso para encontrar todas las ordenes del dia tomando en cuenta las operaciones que se tienen que hacer
                    ordenes = Orden.objects.filter(created_at__day=dia_semana.strftime('%d'),
                                                   created_at__month=dia_semana.strftime('%m'),
                                                   created_at__year=dia_semana.strftime('%Y'), cliente_id=cliente.pk)
                    venta = 0
                    compra = 0
                    if not ordenes:
                        arrSemanaCustomer.append({
                            "dia_semana": dia_semana,
                            "venta": 0,
                            "compra": 0,
                            "utilidad": 0,
                            "margen": 0,
                        })
                    else:
                        # Recorremos las ordenes para ir sumando las compras y ventas del dia
                        for orden in ordenes:
                            venta += int(orden.costo_cliente) + int(orden.costo_adicional_cliente)
                            compra += int(orden.costo_proveedor) + int(orden.costo_adicional_proveedor)
                        if venta == 0 or (venta - compra) == 0:
                            arrSemanaCustomer.append({
                                "dia_semana": dia_semana,
                                "venta": venta,
                                "compra": compra,
                                "utilidad": venta - compra,
                                "margen": 0
                            })
                        else:
                            arrSemanaCustomer.append({
                                "dia_semana": dia_semana,
                                "venta": venta,
                                "compra": compra,
                                "utilidad": venta - compra,
                                "margen": ((venta - compra) / venta ) * 100
                            })
                if ventaSemanalCustomer != 0 :
                    arrSemanaCustomer.append({
                        "dia_semana": "Resultado Semanal",
                        "venta": ventaSemanalCustomer,
                        "compra": compraSemanalCustomer,
                        "utilidad": utilidadSemanalCustomer,
                        "margen": ((ventaSemanalCustomer - compraSemanalCustomer) / ventaSemanalCustomer ) * 100
                    })
                else:
                    arrSemanaCustomer.append({
                        "dia_semana": "Resultado Semanal",
                        "venta": ventaSemanalCustomer,
                        "compra": compraSemanalCustomer,
                        "utilidad": utilidadSemanalCustomer,
                        "margen": 0
                    })
                arrInformacionCustomer.append({
                    "cliente": cliente.nombre,
                    "data": arrSemanaCustomer
                })
            context['ordenes_semana_customer'] = arrInformacionCustomer
        if ventaSemanal != 0 :
            arrInformacion.append({
                "dia_semana": "Resultado Semanal",
                "venta": ventaSemanal,
                "compra": compraSemanal,
                "utilidad": utilidadSemanal,
                "margen": ( (ventaSemanal - compraSemanal) / ventaSemanal ) * 100
            })
        else:
            arrInformacion.append({
                "dia_semana": "Resultado Semanal",
                "venta": ventaSemanal,
                "compra": compraSemanal,
                "utilidad": utilidadSemanal,
                "margen": 0,
            })
        context['noSemanas'] = range(1,53)
        return context
    
    


#################### Procesos para hacer el paginado (SERVERSIDE) de las ordenes ####################


class listadoOrdenesPaginacion(APIView):

    def get(self, request):
        listOrdenes = Orden.objects.all().order_by('-id')
        eqType = self.request.GET.get('eq_type')
        exitAddress = self.request.GET.get('origen')
        destinationAddress = self.request.GET.get('destino')
        listOrdenesEncontradas = []

        # if eqType:
        #         if eqType == '1':
        #             listOrdenes = listOrdenes.filter(eq_type=eqType)
        #         if eqType == '2':
        #             listOrdenes = listOrdenes.filter(Q(eq_type=2) | Q(eq_type=4))
        #         if eqType == '3':
        #             listOrdenes = listOrdenes.filter(Q(eq_type=3) | Q(eq_type=5))
                    
        # if exitAddress and destinationAddress:
        #     for orden in listOrdenes:
        #         points = Orden_Shipper_Delivery.objects.filter(orden_id=orden.pk).values_list('pk')
        #         originDestino = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points)
                
        # elif exitAddress:
        #     for orden in listOrdenes:
        #         points = Orden_Shipper_Delivery.objects.filter(orden_id=orden.pk).values_list('pk')
        #         origin = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points,
        #                                                         tipo=1, ).order_by(
        #             'pk')
        #         if origin:
        #             if origin[0].shipper_delivery.cuidad.pk == int(exitAddress):
        #                 listOrdenesEncontradas.append(orden)
        #     listOrdenes = listOrdenesEncontradas
        # elif destinationAddress:
        #     for orden in listOrdenes:
        #         points = Orden_Shipper_Delivery.objects.filter(orden_id=orden.pk).values_list('pk')
        #         destination = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points,
        #                                                             tipo=2).order_by('pk')
        #         if destination:
        #             if destination[0].shipper_delivery.cuidad.pk == int(destinationAddress):
        #                 listOrdenesEncontradas = list(chain(listOrdenesEncontradas,orden))
            
        #     listOrdenes = listOrdenesEncontradas

        # Agregar paginación
        paginator = Paginator(listOrdenes, 25)  # 10 elementos por página
        page = request.GET.get('page', 1)
        
        try:
            datos_paginados = paginator.page(page)
        except PageNotAnInteger:
            datos_paginados = paginator.page(1)
        except EmptyPage:
            datos_paginados = paginator.page(paginator.num_pages)
        
        return JsonResponse({
            'data': OrdenReporteContabilidadSerializers(datos_paginados,many=True).data,
            'draw': int(request.GET.get('draw', 1)),
            'recordsTotal': listOrdenes.count(),
            'recordsFiltered': paginator.count,
            }, status=200)




#################### Procesos para hacer la vista del calendario semanal de ordenes  ####################

class CalendarioSemanalOrdenes(TemplateView):
    
    template_name= 'calendario.html'
    
    def get_context_data(self, **kwargs):
        context = super(CalendarioSemanalOrdenes, self).get_context_data(**kwargs)
        conection = connection.cursor()
        ordenesAll = []
        for i in range(2):
            year = datetime.now().year
            if i == 1:
                year = year - 1
            query_bd = "select ordenes_calendario('{}')".format(year)
            conection.execute(query_bd)
            query_success = dictfetchall(conection)
            ordenesAll.extend(query_success[0]['ordenes_calendario'])
        context['ordenesAll'] = ordenesAll
        return context
