from rest_framework import serializers

class BusGAInputSerializer(serializers.Serializer):
    students = serializers.ListField()
    buses = serializers.ListField()
    stops = serializers.ListField()
    constraints = serializers.DictField()

class StopSerializer(serializers.Serializer):
    id = serializers.CharField()
    coordinates = serializers.ListField(
        child=serializers.FloatField(), min_length=2, max_length=2

    )
    studentCount = serializers.IntegerField()

class HardConstraintSerializer(serializers.Serializer):
    maxStudentsPerBus = serializers.IntegerField()
    collegeLast = serializers.BooleanField()
    latestArrivalTime = serializers.TimeField(format='%H:%M')

class SoftConstraintSerializer(serializers.Serializer):
    fuelWeight = serializers.FloatField()
    balanceWeight = serializers.FloatField()

class ConstraintSerializer(serializers.Serializer):
    hard = HardConstraintSerializer()
    soft = SoftConstraintSerializer()

class InputDataSerializer(serializers.Serializer):
    stops = StopSerializer(many=True)
    constraints = ConstraintSerializer()
