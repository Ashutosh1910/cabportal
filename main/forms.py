from django import forms
from django.forms import inlineformset_factory
from .models import Route, RouteStop, Travellor, Stop
from .models import Car, CabBooking
import calendar
from datetime import datetime


class TravellorForm(forms.ModelForm):
    """
    Form for creating a new Travellor (trip) instance.
    """
    class Meta:
        model = Travellor
        # Include all non-nullable Travellor fields here. `driver` is
        # excluded because it's set in the view (`request.user`).
        fields = ['route', 'departure_time', 'vehicle_capacity', 'cost_per_km',]
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


class BulkTravellorForm(forms.Form):
    """
    Form for creating daily trips for an entire month.
    """
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
    ]

    route = forms.ModelChoiceField(
        queryset=Route.objects.all(),
        label="Select a Route",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    departure_time = forms.TimeField(
        label="Daily Departure Time",
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        label="Month",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    year = forms.IntegerField(
        label="Year",
        min_value=2024,
        max_value=2100,
        initial=datetime.now().year,
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )
    vehicle_capacity = forms.IntegerField(
        label="Vehicle Capacity",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'e.g., 10'})
    )
    cost_per_km = forms.DecimalField(
        label="Cost per Kilometer",
        max_digits=6,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'e.g., 2.50', 'step': '0.01'})
    )

    def get_days_in_month(self):
        """Returns the number of days in the selected month/year."""
        month = int(self.cleaned_data['month'])
        year = int(self.cleaned_data['year'])
        return calendar.monthrange(year, month)[1]
