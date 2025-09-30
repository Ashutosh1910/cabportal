from django.contrib import admin
from .models import Vendor, Customer, Stop, Route, RouteStop, Travellor, Booking

# To enhance the Route management, we'll show the stops inline
class RouteStopInline(admin.TabularInline):
    """Allows editing RouteStop models directly within the Route admin page."""
    model = RouteStop
    extra = 1  # Provides 1 extra blank form for adding a new stop
    ordering = ('order',)
    # Autocomplete fields can make selecting stops easier if you have many
    autocomplete_fields = ['stop']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    """Custom admin configuration for the Route model."""
    list_display = ('name', 'description')
    search_fields = ('name',)
    inlines = [RouteStopInline]


@admin.register(Travellor)
class TravellorAdmin(admin.ModelAdmin):
    """Custom admin configuration for the Travellor (trip) model."""
    list_display = ('id', 'route', 'driver', 'departure_time', 'vehicle_capacity', 'cost_per_km', 'status')
    list_filter = ('status', 'route', 'driver')
    search_fields = ('route__name', 'driver__username')
    date_hierarchy = 'departure_time'
    ordering = ('-departure_time',)
    autocomplete_fields = ['route', 'driver']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Custom admin configuration for the Booking model."""
    list_display = ('id', 'trip', 'customer', 'start_stop', 'end_stop', 'seats', 'status', 'booking_time')
    list_filter = ('status', 'trip__route', 'customer')
    search_fields = ('customer__name', 'trip__id')
    readonly_fields = ('booking_time',)
    autocomplete_fields = ['trip', 'customer', 'start_stop', 'end_stop']


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    """Custom admin configuration for the Stop model."""
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    """Custom admin configuration for the Vendor model."""
    list_display = ('user', 'company_name', 'contact_number')
    search_fields = ('user__username', 'company_name')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Custom admin configuration for the Customer model."""
    list_display = ('user', 'name', 'contact_number')
    search_fields = ('user__username', 'name')


# Register RouteStop separately to allow individual management if needed,
# though primary management is done via the RouteAdmin inline.
@admin.register(RouteStop)
class RouteStopAdmin(admin.ModelAdmin):
    """Custom admin for direct management of RouteStop entries."""
    list_display = ('route', 'stop', 'order', 'minutes_from_previous_stop', 'distance_from_previous_stop')
    list_filter = ('route',)
    search_fields = ('route__name', 'stop__name')

