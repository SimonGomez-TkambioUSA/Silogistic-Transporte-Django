from rest_framework import serializers
import  random

from apps.catalogo.models import Pais, Estado, Ciudad, TrackingLogOrden, User, Orden, Status_Orden, \
    Orden_Shipper_Delivery, ShipperDeliveryPoints, FormatoCliente


class PaisSerializers(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = '__all__'


class EstadoSerializers(serializers.ModelSerializer):
    pais = PaisSerializers()

    class Meta:
        model = Estado
        fields = '__all__'


class CiudadSerializers(serializers.ModelSerializer):
    estado = EstadoSerializers()

    class Meta:
        model = Ciudad
        fields = '__all__'


class OrdenSerializers(serializers.ModelSerializer):
    class Meta:
        model = Orden
        fields = '__all__'


class StatusOrdenSerializers(serializers.ModelSerializer):
    class Meta:
        model = Status_Orden
        fields = '__all__'


class TrackingLogSerializers(serializers.ModelSerializer):
    register_by = serializers.SerializerMethodField()
    orden = OrdenSerializers()
    status_orden = StatusOrdenSerializers()
    status_po = StatusOrdenSerializers()

    class Meta:
        model = TrackingLogOrden
        fields = '__all__'

    def get_register_by(self, obj):
        user = User.objects.get(pk=obj.register_by)
        return '{} {}'.format(user.first_name, user.last_name)


class OrdenReporteContabilidadSerializers(serializers.ModelSerializer):
    proveedor = serializers.SerializerMethodField()
    origen = serializers.SerializerMethodField()
    destino = serializers.SerializerMethodField()
    costo = serializers.SerializerMethodField()
    eq_type = serializers.SerializerMethodField()
    utilidad = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    

    class Meta:
        model = Orden
        fields = ['id', 'proveedor', 'origen', 'destino', 'costo', 'eq_type','created_at','utilidad','costo_cliente','costo_adicional_cliente','costo_proveedor','costo_adicional_proveedor']

    def get_proveedor(self, obj):
        return obj.proveedor.nombre

    def get_origen(self, obj):
        points = Orden_Shipper_Delivery.objects.filter(orden_id=obj.pk).values_list('pk')
        origin = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points, tipo=1, ).order_by(
            'pk')
        if not origin:
            return 'No aplica'
        return origin[0].shipper_delivery.nombre

    def get_destino(self, obj):
        points = Orden_Shipper_Delivery.objects.filter(orden_id=obj.pk).values_list('pk')
        destination = ShipperDeliveryPoints.objects.filter(order_shipper_delivery_id__in=points, tipo=2).order_by(
            'pk')
        if not destination:
            return 'No aplica'
        return destination[0].shipper_delivery.nombre

    def get_costo(self, obj):
        return obj.costo_proveedor

    def get_eq_type(self, obj):
        return obj.get_eq_type_display()

    def get_utilidad(self,obj):
        return obj.get_utilidad()
    
    def get_created_at(self,obj):
        return obj.created_at.strftime('%B %d, %Y')



class ReporteOrdenesClienteSerializers(serializers.ModelSerializer):

    identificadorReporte = serializers.SerializerMethodField()
    class Meta:
        model = FormatoCliente
        fields = '__all__'

    def get_identificadorReporte(self, obj):
        cadena = ""
        length = [1, 2, 3, 4, 5]
        for let in length:
            cadena = cadena + random.choice("AaBbCcDd1Ee2FfG3gHh45J6j7Kk8M9mNnPpQqRrSsTtUuVvWwXxYyZz")
        cadena = cadena + str(obj.pk)

        for let in length:
            cadena = cadena + random.choice("AaBbCcDd1Ee2FfG3gHh45J6j7Kk8M9mNnPpQqRrSsTtUuVvWwXxYyZz")
        return cadena