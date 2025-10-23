from django import forms
from django.forms import inlineformset_factory
from .models import Route, RouteStop, Travellor, Stop
from .models import Car, CabBooking

class TravellorForm(forms.ModelForm):
    """
    Form for creating a new Travellor (trip) instance.
    """
    class Meta:
        model = Travellor
        fields = ['route', 'departure_time', 'vehicle_capacity']
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['route'].queryset = Route.objects.all()
        self.fields['route'].label = "Select a Route"


class StopForm(forms.ModelForm):
    """
    Form for the main Route details.
    """
    class Meta:
        model = Stop
        fields = ['name', 'description']

class RouteForm(forms.ModelForm):
    """
    Form for the main Route details.
    """
    class Meta:
        model = Route
        fields = ['name', 'description']

class RouteStopForm(forms.ModelForm):
    """
    Form for a single stop within a Route. The 'stop' field
    will allow selecting an existing Stop or creating a new one.
    """
    class Meta:
        model = RouteStop
        fields = ['stop', 'order', 'minutes_from_previous_stop', 'distance_from_previous_stop']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stop'].queryset = Stop.objects.all()


# Create a formset for RouteStop objects related to a Route
RouteStopFormSet = inlineformset_factory(
    Route,          # Parent model
    RouteStop,      # Inline model
    form=RouteStopForm,
    extra=1,        # Number of empty forms to display
    can_delete=True,
    can_order=False, # We use the 'order' field for explicit ordering
    fk_name='route',
    fields=['stop', 'order', 'minutes_from_previous_stop', 'distance_from_previous_stop']
)


class CarForm(forms.ModelForm):
    """
    Form for creating or editing a Car.
    """
    class Meta:
        model = Car
        fields = ['name', 'license_plate']


class CabBookingConfirmForm(forms.ModelForm):
    """
    Form used by vendors to confirm a CabBooking by assigning a car and driver details.
    """
    class Meta:
        model = CabBooking
        fields = ['car', 'driver_name', 'driver_no', ]
