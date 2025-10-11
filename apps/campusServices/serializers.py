from rest_framework import serializers
from apps.campusServices.models import SportPlace, LibraryBook, TransportLine, Notification, WifiHotspot


class SportPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportPlace
        fields = '__all__'


class LibraryBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryBook
        fields = '__all__'


class TransportLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportLine
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class WifiHotspotSerializer(serializers.ModelSerializer):
    class Meta:
        model = WifiHotspot
        fields = '__all__'
