from rest_framework import serializers
from .models import Booking, Travellor, Stop, RouteStop, Customer, Car, CabBooking
from django.contrib.auth.models import User
from django.db.models import Sum


class BookingSerializer(serializers.ModelSerializer):
    start_stop = serializers.PrimaryKeyRelatedField(queryset=RouteStop.objects.all())
    end_stop = serializers.PrimaryKeyRelatedField(queryset=RouteStop.objects.all())

    class Meta:
        model = Booking
        fields = ['id', 'trip', 'customer', 'start_stop', 'end_stop', 'seats', 'status', 'booking_time']
        read_only_fields = ('id', 'customer', 'status', 'booking_time')

    def validate(self, data):
        """
        Check that the start stop is before the end stop.
        """
        if data['start_stop'].order >= data['end_stop'].order:
            raise serializers.ValidationError("End stop must be after start stop.")
        
        if data['start_stop'].route != data['trip'].route or data['end_stop'].route != data['trip'].route:
            raise serializers.ValidationError("Stops must be on the trip's route.")

        return data


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'contact_number']


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['id', 'name', 'description']


class RouteStopSerializer(serializers.ModelSerializer):
    stop = StopSerializer(read_only=True)
    estimated_arrival_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = RouteStop
        fields = ['id', 'stop', 'order', 'minutes_from_previous_stop', 'distance_from_previous_stop', 'estimated_arrival_time']


class TravellorSerializer(serializers.ModelSerializer):
    route_stops = serializers.SerializerMethodField()
    driver_name = serializers.CharField(source='driver.username', read_only=True)
    route_name = serializers.CharField(source='route.name', read_only=True)
    price = serializers.SerializerMethodField()

    class Meta:
        model = Travellor
        fields = ['id', 'driver_name', 'route_name', 'departure_time', 'vehicle_capacity', 'status', 'route_stops', 'cost_per_km', 'price']

    def get_route_stops(self, obj):
        schedule = obj.get_schedule()
        route_stop_ids = [item['route_stop_id'] for item in schedule]
        route_stops = RouteStop.objects.filter(id__in=route_stop_ids).order_by('order')
        
        for rs in route_stops:
            for item in schedule:
                if rs.id == item['route_stop_id']:
                    rs.estimated_arrival_time = item['estimated_arrival_time']
                    break
        
        return RouteStopSerializer(route_stops, many=True).data

    def get_price(self, obj):
        # start_stop_id = self.context.get('start_stop_id')
        # end_stop_id = self.context.get('end_stop_id')

        # if not start_stop_id or not end_stop_id:
        #     return None

        # try:
        #     start_stop = RouteStop.objects.get(route=obj.route, stop_id=start_stop_id)
        #     end_stop = RouteStop.objects.get(route=obj.route, stop_id=end_stop_id)
        # except RouteStop.DoesNotExist:
        #     return None

        # if start_stop.order >= end_stop.order:
        #     return None

        # total_distance = RouteStop.objects.filter(
        #     route=obj.route,
        #     order__gt=start_stop.order,
        #     order__lte=end_stop.order
        # ).aggregate(total=Sum('distance_from_previous_stop'))['total'] or 0

        return obj.cost_per_km



class BookingDetailSerializer(serializers.ModelSerializer):
    trip = TravellorSerializer(read_only=True)
    start_stop = StopSerializer(source='start_stop.stop', read_only=True)
    end_stop = StopSerializer(source='end_stop.stop', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    estimated_departure = serializers.SerializerMethodField()
    estimated_arrival = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 
            'trip', 
            'customer_name', 
            'start_stop', 
            'end_stop', 
            'seats', 
            'status', 
            'booking_time',
            'estimated_departure',
            'estimated_arrival',
            'price'
        ]

    def get_estimated_departure(self, obj):
        schedule = obj.trip.get_schedule()
        start_stop_schedule = next((item for item in schedule if item['route_stop_id'] == obj.start_stop.id), None)
        return start_stop_schedule['estimated_arrival_time'] if start_stop_schedule else None

    def get_estimated_arrival(self, obj):
        schedule = obj.trip.get_schedule()
        end_stop_schedule = next((item for item in schedule if item['route_stop_id'] == obj.end_stop.id), None)
        return end_stop_schedule['estimated_arrival_time'] if end_stop_schedule else None

    def get_price(self, obj):
        start_stop = obj.start_stop
        end_stop = obj.end_stop
        trip = obj.trip

        if not all([start_stop, end_stop, trip]):
            return None

        total_distance = RouteStop.objects.filter(
            route=trip.route,
            order__gt=start_stop.order,
            order__lte=end_stop.order
        ).aggregate(total=Sum('distance_from_previous_stop'))['total'] or 0

        price_per_seat = total_distance * trip.cost_per_km
        return price_per_seat * obj.seats


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'name', 'license_plate']


class CabBookingSerializer(serializers.ModelSerializer):
    # Expose car id for selection and allow driver fields to be returned
    # For customer booking, they provide people_count (number of passengers).
    # `car` remains optional but is not required when creating a booking.
    car = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all(), required=False, allow_null=True)
    people_count = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = CabBooking
        fields = ['id', 'customer', 'pickup_location', 'dropoff_location', 'pickup_time', 'people_count', 'status', 'driver_no', 'driver_name', 'car', 'booking_time']
        read_only_fields = ('id', 'customer', 'status', 'booking_time','driver_no', 'driver_name', 'car',)

    def validate(self, data):
        # pickup_time should be provided
        pickup_time = data.get('pickup_time')
        if pickup_time is None:
            raise serializers.ValidationError({'pickup_time': 'Pickup time is required.'})

        # people_count must be a positive integer
        people_count = data.get('people_count')
        if people_count is None:
            raise serializers.ValidationError({'people_count': 'people_count is required.'})
        if not isinstance(people_count, int) or people_count < 1:
            raise serializers.ValidationError({'people_count': 'people_count must be an integer >= 1.'})

        # Additional validations can be added here (e.g., location checks)
        return data

    def create(self, validated_data, **kwargs):
        # allow view to pass customer via save(customer=...)
        customer = kwargs.pop('customer', None)
        if customer is None:
            raise serializers.ValidationError('Customer must be provided')
        validated_data['customer'] = customer
        return super().create(validated_data)


class CabBookingDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    car = CarSerializer(read_only=True)
    people_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = CabBooking
        fields = ['id', 'customer', 'pickup_location', 'dropoff_location', 'pickup_time', 'people_count', 'booking_time', 'status', 'driver_no', 'driver_name', 'car']
