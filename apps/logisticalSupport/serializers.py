from rest_framework import serializers
from apps.logisticalSupport.models import Facility, Maintenance, CanteenMenu, CleaningTask, SecurityEvent


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = '__all__'


class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = '__all__'


class CanteenMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = CanteenMenu
        fields = '__all__'


class CleaningTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CleaningTask
        fields = '__all__'


class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = '__all__'
