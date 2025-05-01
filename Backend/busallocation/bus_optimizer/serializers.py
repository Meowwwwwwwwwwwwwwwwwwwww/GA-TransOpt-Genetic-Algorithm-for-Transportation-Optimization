from rest_framework import serializers

class BusSerializer(serializers.Serializer):
    id = serializers.CharField()
    capacity = serializers.IntegerField()
    depotCoordinates = serializers.ListField(child=serializers.FloatField())

class StopSerializer(serializers.Serializer):
    id = serializers.CharField()
    coordinates = serializers.ListField(child=serializers.FloatField())
    studentCount = serializers.IntegerField()

class ConstraintsSerializer(serializers.Serializer):
    hard = serializers.DictField()
    soft = serializers.DictField()

class BusGAInputSerializer(serializers.Serializer):
    buses = BusSerializer(many=True)
    stops = StopSerializer(many=True)
    constraints = ConstraintsSerializer()
