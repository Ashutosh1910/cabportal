from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
from datetime import timedelta

# Create your models here.

class Vendor(models.Model):
    """
    Represents a vendor or a company that owns vehicles and employs drivers.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    company_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name

class Customer(models.Model):
    """
    Represents a customer who books rides.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Stop(models.Model):
    """
    Represents a physical stop or landmark.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text="e.g., 'Near the main post office'")

    def __str__(self):
        return self.name

class Route(models.Model):
    """
    Represents a predefined route consisting of an ordered sequence of stops.
    """
    name = models.CharField(max_length=255, help_text="e.g., 'City Center to Airport'")
    stops = models.ManyToManyField(Stop, through='RouteStop', related_name='routes')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class RouteStop(models.Model):
    """
    A 'through' model to link Stops to Routes, defining the order of stops in a route.
    """
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(help_text="The sequence number of the stop in the route (e.g., 1, 2, 3).")
    minutes_from_previous_stop = models.PositiveIntegerField(
        default=0,
        help_text="Time in minutes to reach this stop from the immediate previous stop. Set to 0 for the first stop."
    )
    distance_from_previous_stop = models.IntegerField(
        default=0,
        help_text="Distance in kilometers from the immediate previous stop. Set to 0 for the first stop."
    )

    class Meta:
        ordering = ['route', 'order']
        unique_together = ('route', 'order')

    def __str__(self):
        return f"{self.route.name} - Stop {self.order}: {self.stop.name}"

    def clean(self):
        """
        Ensures that the first stop has 0 travel time and distance, and subsequent stops have non-zero values.
        """
        if self.order == 1:
            if self.minutes_from_previous_stop != 0:
                raise ValidationError("The first stop (order=1) must have 0 minutes from the previous stop.")
            if self.distance_from_previous_stop != 0:
                raise ValidationError("The first stop (order=1) must have 0.0 km distance from the previous stop.")
        else:
            if self.minutes_from_previous_stop == 0:
                raise ValidationError("Only the first stop can have 0 minutes from the previous stop.")
            if self.distance_from_previous_stop == 0:
                raise ValidationError("Only the first stop can have 0.0 km distance from the previous stop.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Travellor(models.Model):
    """
    Represents a specific trip or journey undertaken by a driver along a predefined route.
    This is the entity that customers can book seats on.
    """
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips_as_driver')
    route = models.ForeignKey(Route, on_delete=models.PROTECT, related_name='trips')
    departure_time = models.DateTimeField()
    vehicle_capacity = models.PositiveIntegerField()
    cost_per_km = models.DecimalField(max_digits=6, decimal_places=2, help_text="Cost per kilometer for this trip.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')

    def __str__(self):
        return f"Trip on {self.route.name} by {self.driver.username} at {self.departure_time.strftime('%Y-%m-%d %H:%M')}"

    def get_booked_seats_for_segment(self, start_stop_order, end_stop_order):
        """
        Calculates the maximum number of concurrent bookings for any part of a given trip segment.
        A segment is defined by the journey between a start and end stop.
        """
        max_booked = 0
        # Iterate through each leg of the journey within the requested segment
        for i in range(start_stop_order, end_stop_order):
            leg_start_order = i
            leg_end_order = i + 1

            # Find bookings that are active during this specific leg
            concurrent_bookings = self.bookings.filter(
                status='CONFIRMED',
                start_stop__order__lte=leg_start_order,
                end_stop__order__gte=leg_end_order
            ).aggregate(total_seats=Sum('seats'))

            current_leg_seats = concurrent_bookings['total_seats'] or 0
            if current_leg_seats > max_booked:
                max_booked = current_leg_seats
        return max_booked

    def get_schedule(self):
        """
        Calculates the estimated arrival time for each stop on the trip's route.
        Returns a list of dictionaries, each containing the stop and its ETA.
        """
        schedule = []
        # Fetch related stop objects to avoid N+1 queries in the loop
        route_stops = self.route.routestop_set.select_related('stop').all().order_by('order')
        total_travel_minutes = 0

        for rs in route_stops:
            total_travel_minutes += rs.minutes_from_previous_stop
            eta = self.departure_time + timedelta(minutes=total_travel_minutes)
            schedule.append({
                'route_stop_id': rs.id,
                'stop_id': rs.stop.id,
                'stop_name': rs.stop.name,
                'order': rs.order,
                'estimated_arrival_time': eta
            })
        return schedule


class Booking(models.Model):
    """
    Represents a booking made by a customer for a specific trip (Travellor instance).
    """
    STATUS_CHOICES = [
        ('COMPLETED', 'Completed'),
        ('CONFIRMED', 'Confirmed'),
        
    ]
    trip = models.ForeignKey(Travellor, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    start_stop = models.ForeignKey(RouteStop, on_delete=models.PROTECT, related_name='booking_starts')
    end_stop = models.ForeignKey(RouteStop, on_delete=models.PROTECT, related_name='booking_ends')
    seats = models.PositiveIntegerField(default=1)
    booking_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')

    def __str__(self):
        return f"Booking by {self.customer.name} on trip {self.trip.id} for {self.seats} seat(s)"

    def clean(self):
        """
        Custom validation for the booking model.
        """
        # 1. Check if stops belong to the trip's route
        if self.start_stop.route != self.trip.route or self.end_stop.route != self.trip.route:
            raise ValidationError("Start and end stops must belong to the trip's route.")

        # 2. Check if the start stop comes before the end stop
        if self.start_stop.order >= self.end_stop.order:
            raise ValidationError("The start stop must be before the end stop in the route.")

        # 3. Check for seat availability for the entire segment of this booking
        # Note: This check doesn't account for other concurrent unsaved bookings.
        # A more robust solution might use transaction locking or signals.
        if self.pk is None: # Only run for new bookings
            max_concurrent_seats = self.trip.get_booked_seats_for_segment(self.start_stop.order, self.end_stop.order)
            available_seats = self.trip.vehicle_capacity - max_concurrent_seats
            if self.seats > available_seats:
                raise ValidationError(f"Not enough seats available. Only {available_seats} seat(s) left for this segment.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Car(models.Model):
    name=models.CharField(max_length=100)
    license_plate=models.CharField(max_length=20)
    
    
    def __str__(self):
        return f"{self.name} ({self.license_plate})"
    

class CabBooking(models.Model):
    """
    Represents a cab booking made by a customer.
    """
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('BOOKED', 'Booked'),
        ('CANCELLED', 'Cancelled'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cab_bookings')
    pickup_location = models.TextField()
    dropoff_location = models.TextField()
    pickup_time = models.DateTimeField()
    people_count = models.PositiveIntegerField(default=1)
    booking_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='BOOKED')
    driver_no=models.CharField(max_length=15,null=True,blank=True)
    driver_name=models.CharField(max_length=100,null=True,blank=True)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='cab_bookings',null=True,blank=True)

    def __str__(self):
        return f"Cab booking by {self.customer.name} from {self.pickup_location} to {self.dropoff_location}"


