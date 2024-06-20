from django.contrib.auth.models import AbstractUser
from django.db import models
import random


# from apps.catalogo.serializers import ContactoClienteSerializers


class User(AbstractUser):
    administrador = models.BooleanField(default=False)
    ejecutivo = models.BooleanField(default=False)
    cliente = models.BooleanField(default=False)


class Cliente(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    nombre_corto = models.CharField(max_length=50, null=True, blank=True)
    direccion = models.CharField(max_length=150, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)

    def get_dates_contacto(self):
        contacto = Contacto_Cliente.objects.filter(cliente_id=self.pk).order_by('-pk').first()
        return contacto

    def get_contactos(self):
        list_contactos = []

        contactos = Contacto_Cliente.objects.filter(cliente_id=self.pk).order_by('-pk')
        for contacto in contactos:
            list_contactos.append({
                "id": contacto.pk,
                "nombre": contacto.nombre,
                "correo": contacto.correo,
                "telefono": contacto.telefono
            })
        return list_contactos


class Contacto_Cliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    correo = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)


class Producto(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    nombre_corto = models.CharField(max_length=50, null=True, blank=True)
    sku = models.CharField(max_length=50, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)


class Pais(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    clave = models.CharField(max_length=20, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)


class Estado(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    clave = models.CharField(max_length=20, null=True, blank=True)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)


class Ciudad(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    clave = models.CharField(max_length=20, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, null=True, blank=True)
    activo = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    nombre_corto = models.CharField(max_length=50, null=True, blank=True)
    direccion = models.CharField(max_length=150, null=True, blank=True)
    calle = models.CharField(max_length=150, null=True, blank=True)
    numero = models.CharField(max_length=150, null=True, blank=True)
    cp = models.CharField(max_length=150, null=True, blank=True)
    cuidad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)

    def get_contactos(self):
        list_contactos = []

        contactos = ContactoProveedor.objects.filter(proveedor_id=self.pk).order_by('-pk')
        for contacto in contactos:
            list_contactos.append({
                "pk": contacto.pk,
                "nombre": contacto.nombre,
                "puesto": contacto.puesto,
                "correo": contacto.email,
                "numero": contacto.celular,
            })
        return list_contactos


class ContactoProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=150, null=True, blank=True)
    puesto = models.CharField(max_length=150, null=True, blank=True)
    celular = models.CharField(max_length=150, null=True, blank=True)
    email = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)


class Shipper_Delivery(models.Model):
    TIPO = (
        (1, 'Shipper'),
        (2, 'Delivery'),
        (3, 'Shipper/Delivery')
    )
    nombre = models.CharField(max_length=100, null=True, blank=True)
    cp = models.CharField(max_length=20, null=True, blank=True)
    cuidad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, null=True, blank=True)
    direccion = models.CharField(max_length=150, null=True, blank=True)
    c_nombre = models.CharField(max_length=150, null=True, blank=True)
    c_telefono = models.CharField(max_length=20, null=True, blank=True)
    c_email = models.CharField(max_length=150, null=True, blank=True)
    tipo = models.PositiveSmallIntegerField(choices=TIPO, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)


class Status_Orden(models.Model):
    descripcion = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)


class Orden(models.Model):
    EQ_TYPE = (
        (1, "22' VAN"),
        (2, "48' DRY VAN"),
        (3, "48' REEFER"),
        (4, "53' DRY VAN"),
        (5, "53' REEFER"),
    )
    TIPO_CAMBIO = (
        (1, "USD"),
        (2, "MXN"),
    )

    LOAD_TYPE = (
        (1, "NORMAL"),
        (2, "EXTRA"),
        (3, "EXPORTACIÓN"),
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True, blank=True)
    costo_cliente = models.CharField(max_length=50, null=True, blank=True, default=0)
    costo_proveedor = models.CharField(max_length=50, null=True, blank=True, default=0)
    costo_adicional_cliente = models.CharField(max_length=50, null=True, blank=True, default=0)
    costo_adicional_proveedor = models.CharField(max_length=50, null=True, blank=True, default=0)
    wo = models.CharField(max_length=50, null=True, blank=True)
    direccion_origen = models.CharField(max_length=300, null=True, blank=True)
    direccion_destino = models.CharField(max_length=300, null=True, blank=True)
    eq_type = models.PositiveSmallIntegerField(choices=EQ_TYPE, null=True, blank=True)
    tipo_cambio = models.PositiveSmallIntegerField(choices=TIPO_CAMBIO, null=True, blank=True)
    pedimento = models.CharField(max_length=100, null=True, blank=True)
    pro = models.CharField(max_length=100, null=True, blank=True)
    load = models.CharField(max_length=100, null=True, blank=True)
    mx_truck_num = models.CharField(max_length=100, null=True, blank=True)
    us_truck_num = models.CharField(max_length=100, null=True, blank=True)
    load_type = models.PositiveSmallIntegerField(choices=LOAD_TYPE, null=True, blank=True)
    mx_plate_num = models.CharField(max_length=100, null=True, blank=True)
    us_plate_num = models.CharField(max_length=100, null=True, blank=True)
    realase = models.CharField(max_length=100, null=True, blank=True)
    mx_driver_one = models.CharField(max_length=100, null=True, blank=True)
    mx_driver_phone_one = models.CharField(max_length=100, null=True, blank=True)
    mx_driver_two = models.CharField(max_length=100, null=True, blank=True)
    mx_driver_phone_two = models.CharField(max_length=100, null=True, blank=True)
    us_driver_one = models.CharField(max_length=100, null=True, blank=True)
    us_driver_phone_one = models.CharField(max_length=100, null=True, blank=True)
    us_driver_two = models.CharField(max_length=100, null=True, blank=True)
    us_driver_phone_two = models.CharField(max_length=100, null=True, blank=True)
    vin = models.CharField(max_length=100, null=True, blank=True)
    lms = models.CharField(max_length=100, null=True, blank=True)
    invoice = models.CharField(max_length=100, null=True, blank=True)
    empty_truck = models.CharField(max_length=100, null=True, blank=True)
    invoice_date = models.DateTimeField(null=True, blank=True)
    notif_docs = models.DateTimeField(null=True, blank=True)
    cma = models.CharField(max_length=100, null=True, blank=True)
    maniobras = models.CharField(max_length=100, null=True, blank=True)
    estancias = models.CharField(max_length=100, null=True, blank=True)
    otros = models.CharField(max_length=100, null=True, blank=True)
    arrival = models.DateTimeField(null=True, blank=True)
    loading_time = models.CharField(max_length=100, null=True, blank=True)
    waiting = models.CharField(max_length=100, null=True, blank=True)
    crossing_time = models.CharField(max_length=100, null=True, blank=True)
    serie = models.CharField(max_length=100, null=True, blank=True)
    folio = models.CharField(max_length=100, null=True, blank=True)
    uuid = models.CharField(max_length=100, null=True, blank=True)
    activo = models.BooleanField(default=True)
    status_orden = models.ForeignKey(Status_Orden, on_delete=models.CASCADE, null=True, blank=True)
    status_po = models.ForeignKey(Status_Orden, on_delete=models.CASCADE, related_name="po_status", null=True,
                                  blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)
    # Campos agregados para la parte de contabilidad
    cliente_factura = models.CharField(max_length=100, null=True, blank=True)
    cliente_factura_fecha = models.DateTimeField(null=True, blank=True)
    cliente_pago_fecha = models.DateTimeField(null=True, blank=True)
    cliente_cantidad = models.CharField(max_length=100, null=True, blank=True)
    factoraje_fecha_deposito = models.DateTimeField(null=True, blank=True)
    factoraje_monto = models.CharField(max_length=100, null=True, blank=True)
    saldo = models.CharField(max_length=100, null=True, blank=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    monto_pago = models.CharField(max_length=100, null=True, blank=True)
    pago_factoraje_fecha = models.DateTimeField(null=True, blank=True)
    pago_factoraje_referencia = models.CharField(max_length=100, null=True, blank=True)
    pago_factoraje_monto = models.CharField(max_length=100, null=True, blank=True)
    proovedor_factura = models.CharField(max_length=100, null=True, blank=True)
    proovedor_monto = models.CharField(max_length=100, null=True, blank=True)
    proveedor_pago_fecha = models.DateTimeField(null=True, blank=True)
    proveedor_pago_monto = models.CharField(max_length=100, null=True, blank=True)

    # Campos Adicionales para el reporte dle cliente
    esj_po = models.CharField(max_length=100, null=True, blank=True)
    flatbed = models.CharField(max_length=100, null=True, blank=True)
    carrier_mx = models.CharField(max_length=100, null=True, blank=True)
    carrier_usa = models.CharField(max_length=100, null=True, blank=True)
    loading_warehouse = models.DateTimeField(null=True, blank=True)
    departure_esj = models.DateTimeField(null=True, blank=True)
    arrival_juarez = models.DateTimeField(null=True, blank=True)
    arrival_el_paso = models.DateTimeField(null=True, blank=True)
    departure_usa = models.DateTimeField(null=True, blank=True)
    arrival_destination = models.DateTimeField(null=True, blank=True)
    
    # Campos nuevos de monto
    cliente_iva_retenido = models.CharField(max_length=100, null=True, blank=True, default='0')
    cliente_iva_trasladado = models.CharField(max_length=100, null=True, blank=True, default='0')
    cliente_subtotal_monto = models.CharField(max_length=100, null=True, blank=True, default='0')
    cliente_tipo_cambio = models.PositiveSmallIntegerField(choices=TIPO_CAMBIO, null=True, blank=True)
    
    cliente_tipo_cambio = models.PositiveSmallIntegerField(choices=TIPO_CAMBIO, null=True, blank=True)
    proveedor_tipo_cambio = models.PositiveSmallIntegerField(choices=TIPO_CAMBIO, null=True, blank=True)
    

    def get_name_register_by(self):
        user = User.objects.get(pk=self.register_by)
        return '{} {}'.format(user.first_name, user.last_name)

    def get_shippdate(self):
        points = Orden_Shipper_Delivery.objects.filter(orden_id=self.pk).values_list('pk')
        dates_shipp = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points, tipo=1, ).order_by(
            'pk')
        if not dates_shipp:
            return 'No aplica'
        return dates_shipp[0].date

    def get_origin(self):
        points = Orden_Shipper_Delivery.objects.filter(orden_id=self.pk).values_list('pk')
        origin = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points, tipo=1, ).order_by(
            'pk')
        if not origin:
            return 'No aplica'
        return origin[0].shipper_delivery.cuidad.nombre + ' - ' + origin[0].shipper_delivery.cuidad.estado.clave

    def get_carrier(self):
        points = Orden_Shipper_Delivery.objects.filter(orden_id=self.pk).values_list('pk')
        origin = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points, tipo=1, ).order_by(
            'pk')
        if not origin:
            return 'No aplica'
        return origin[0].shipper_delivery

    def get_destination(self):
        points = Orden_Shipper_Delivery.objects.filter(orden_id=self.pk).values_list('pk')
        destination = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points, tipo=2).order_by(
            'pk')
        if not destination:
            return 'No aplica'
        return destination[0].shipper_delivery.cuidad.nombre + ' - ' + destination[0].shipper_delivery.cuidad.estado.clave

    def get_delivery(self):
        points = Orden_Shipper_Delivery.objects.filter(orden_id=self.pk).values_list('pk')
        destination = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points, tipo=2).order_by(
            'pk')
        if not destination:
            return 'No aplica'
        return destination[0].shipper_delivery

    def get_producto(self):
        points = Orden_Shipper_Delivery.objects.filter(orden_id=self.pk)
        return points[0]

    def get_deliverydate(self):
        points = Orden_Shipper_Delivery.objects.filter(orden_id=self.pk).values_list('pk')
        dates_shipp = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points, tipo=2).order_by(
            'pk')
        if not dates_shipp:
            return 'No aplica'
        return dates_shipp[0].date

    def get_utilidad(self):
        venta = int(self.costo_cliente)
        compra = int(self.costo_proveedor)

        if (self.costo_adicional_cliente):
            venta += int(self.costo_adicional_cliente)

        if self.costo_adicional_proveedor:
            compra += int(self.costo_adicional_proveedor)
        return venta - compra


class Orden_Shipper_Delivery(models.Model):
    TYPE = (
        (1, "TL"),
        (2, "LTL"),
        (3, "PALLETS"),
        (4, "BAGS"),
    )

    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, null=True, blank=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.PositiveSmallIntegerField(choices=TYPE, null=True, blank=True)
    qty = models.CharField(max_length=100, null=True, blank=True)
    weight = models.CharField(max_length=100, null=True, blank=True)
    precio = models.CharField(max_length=100, null=True, blank=True)
    po_numbers = models.CharField(max_length=100, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)


class ShipperDeliveryPoints(models.Model):
    TYPE = (
        (1, "Shipper"),
        (2, "Delivery"),
    )

    order_shipper_delivery = models.ForeignKey(Orden_Shipper_Delivery, on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.PositiveSmallIntegerField(choices=TYPE, null=True, blank=True)
    shipper_delivery = models.ForeignKey(Shipper_Delivery, on_delete=models.CASCADE, null=True,
                                         blank=True)
    date = models.DateTimeField(null=True, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)


class PersonaSistema(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    ap_paterno = models.CharField(max_length=100, null=True, blank=True)
    ap_materno = models.CharField(max_length=100, null=True, blank=True)
    correo = models.CharField(max_length=200, null=True, blank=True)
    usuario = models.ForeignKey('catalogo.User', on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey('catalogo.Cliente', on_delete=models.CASCADE, null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)


class TrackingLogOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, null=True, blank=True)
    status_orden = models.ForeignKey(Status_Orden, on_delete=models.CASCADE, null=True, blank=True)
    status_po = models.ForeignKey(Status_Orden, on_delete=models.CASCADE, related_name="po_status_tracking", null=True,
                                  blank=True)
    nota = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    register_by = models.IntegerField(null=True, blank=True)


class FormatoCliente(models.Model):
    cliente = models.ForeignKey('catalogo.Cliente', on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)

    def get_campos(self):
        arrCampos = []
        camposFormatos = CamposFormatosClientes.objects.filter(formato_id=self.pk)
        for campos in camposFormatos:
            arrCampos.append(campos.campo.nombre)
        return arrCampos

    def get_campos_acceso(self):
        arrCampos = []
        camposFormatos = CamposFormatosClientes.objects.filter(formato_id=self.pk)
        for campos in camposFormatos:
            arrCampos.append(campos.campo.acceso)
        return arrCampos

    def get_identificadorReporte(self):
        cadena = ""
        length = [1, 2, 3, 4, 5]
        for let in length:
            cadena = cadena + random.choice("AaBbCcDd1Ee2FfG3gHh45J6j7Kk8M9mNnPpQqRrSsTtUuVvWwXxYyZz")
        cadena = cadena + str(self.pk)

        for let in length:
            cadena = cadena + random.choice("AaBbCcDd1Ee2FfG3gHh45J6j7Kk8M9mNnPpQqRrSsTtUuVvWwXxYyZz")
        return cadena


class CamposDisponiblesSistema(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    acceso = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    register_by = models.IntegerField(null=True, blank=True)


class CamposFormatosClientes(models.Model):
    formato = models.ForeignKey('catalogo.FormatoCliente', on_delete=models.CASCADE, null=True, blank=True)
    campo = models.ForeignKey('catalogo.CamposDisponiblesSistema', on_delete=models.CASCADE, null=True, blank=True)
