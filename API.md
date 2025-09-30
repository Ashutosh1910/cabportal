# API Documentation

This document provides documentation for all the API endpoints in the Cab Portal application.

## Authentication

### Google Login

*   **URL**: `/auth/google/`
*   **Method**: `POST`
*   **Description**: Authenticates a user using a Google ID token. If the user does not exist, a new user is created. It returns a JWT access and refresh token.
*   **Permissions**: None
*   **Request Body**:
    *   `token` (string, required): The ID token obtained from Google after a successful sign-in.
    ```json
    {
        "token": "your_google_id_token"
    }
    ```
*   **Success Response (200 OK)**:
    *   `refresh` (string): A refresh token for obtaining new access tokens.
    *   `access` (string): An access token for authenticating subsequent requests.
    *   `customer` (object | null): The customer profile if it exists, otherwise `null`.
    ```json
    {
        "refresh": "...",
        "access": "...",
        "customer": {
            "name": "Ashutosh",
            "contact_number": "1234567890"
        }
    }
    ```
*   **Error Response (400 Bad Request)**:
    ```json
    {
        "error": "Google token is required"
    }
    ```
*   **Error Response (401 Unauthorized)**:
    ```json
    {
        "error": "Invalid Google token"
    }
    ```

---

## Customer

### Customer Signup

*   **URL**: `/customer-signup/`
*   **Method**: `POST`
*   **Description**: Creates a customer profile for an authenticated user. This endpoint should be used after a user has logged in with Google but before they have created a customer profile.
*   **Permissions**: `IsAuthenticated`
*   **Request Body**:
    *   `name` (string, required): The full name of the customer.
    *   `contact_number` (string, required): The contact number of the customer.
    ```json
    {
        "name": "Ashutosh",
        "contact_number": "1234567890"
    }
    ```
*   **Success Response (201 Created)**:
    *   Returns the created customer profile.
    ```json
    {
        "name": "Ashutosh",
        "contact_number": "1234567890"
    }
    ```
*   **Error Response (400 Bad Request)**:
    ```json
    {
        "error": "Customer profile already exists."
    }
    ```

---

## Bookings

### Book a Trip

*   **URL**: `/book-traveller/`
*   **Method**: `POST`
*   **Description**: Books a trip for the authenticated user. The user must have a customer profile.
*   **Permissions**: `IsAuthenticated`
*   **Request Body**:
    *   `trip` (integer, required): The ID of the `Travellor` (trip) to book.
    *   `start_stop` (integer, required): The ID of the `RouteStop` where the user will start the trip.
    *   `end_stop` (integer, required): The ID of the `RouteStop` where the user will end the trip.
    *   `seats` (integer, required): The number of seats to book.
    ```json
    {
        "trip": 1,
        "start_stop": 1,
        "end_stop": 2,
        "seats": 1
    }
    ```
*   **Success Response (201 Created)**:
    *   Returns a `Booking` object with the details of the new booking.
    ```json
    {
        "id": 1,
        "trip": 1,
        "customer": 1,
        "start_stop": 1,
        "end_stop": 2,
        "seats": 1,
        "status": "CONFIRMED",
        "booking_time": "2025-09-25T10:00:00Z"
    }
    ```
*   **Error Response (400 Bad Request)**:
    ```json
    {
        "error": "Not enough seats available. Only 2 seat(s) left for this segment."
    }
    ```

### View User Bookings

*   **URL**: `/my-bookings/`
*   **Method**: `GET`
*   **Description**: Retrieves a list of all bookings for the currently authenticated user.
*   **Permissions**: `IsAuthenticated`
*   **Success Response (200 OK)**:
    *   Returns a list of `BookingDetail` objects.
    ```json
    [
        {
            "id": 1,
            "trip": {
                "id": 1,
                "driver_name": "vendor_user",
                "route_name": "City Center to Airport",
                "departure_time": "2025-10-01T09:00:00Z",
                "vehicle_capacity": 10,
                "status": "SCHEDULED",
                "cost_per_km": "2.50",
                "price": "75.00",
                "route_stops": [
                    {
                        "id": 1,
                        "stop": {
                            "id": 1,
                            "name": "City Center",
                            "description": ""
                        },
                        "order": 1,
                        "minutes_from_previous_stop": 0,
                        "distance_from_previous_stop": 0,
                        "estimated_arrival_time": "2025-10-01T09:00:00Z"
                    }
                ]
            },
            "customer_name": "Ashutosh",
            "start_stop": {
                "id": 1,
                "name": "City Center",
                "description": ""
            },
            "end_stop": {
                "id": 2,
                "name": "Airport",
                "description": ""
            },
            "seats": 1,
            "status": "CONFIRMED",
            "booking_time": "2025-09-25T10:00:00Z",
            "estimated_departure": "2025-10-01T09:00:00Z",
            "estimated_arrival": "2025-10-01T09:30:00Z",
            "price": "75.00"
        }
    ]
    ```

---

## Travellers and Routes

### Search for Travellers

*   **URL**: `/search-travellers/`
*   **Method**: `GET`
*   **Description**: Searches for available travellers between two stops.
*   **Permissions**: `IsAuthenticated`
*   **Query Parameters**:
    *   `start_stop_id` (integer, required): The ID of the start `Stop`.
    *   `end_stop_id` (integer, required): The ID of the end `Stop`.
*   **Success Response (200 OK)**:
    *   Returns a list of `Travellor` objects that match the search criteria.
    ```json
    [
        {
            "id": 1,
            "driver_name": "vendor_user",
            "route_name": "City Center to Airport",
            "departure_time": "2025-10-01T09:00:00Z",
            "vehicle_capacity": 10,
            "status": "SCHEDULED",
            "cost_per_km": "2.50",
            "price": "75.00",
            "route_stops": [
                {
                    "id": 1,
                    "stop": {
                        "id": 1,
                        "name": "City Center",
                        "description": ""
                    },
                    "order": 1,
                    "minutes_from_previous_stop": 0,
                    "distance_from_previous_stop": 0,
                    "estimated_arrival_time": "2025-10-01T09:00:00Z"
                }
            ],
            "departure_from_start": "2025-10-01T09:00:00Z",
            "arrival_at_end": "2025-10-01T09:30:00Z",
            "start_stop_id": 1,
            "end_stop_id": 2
        }
    ]
    ```

### List All Stops

*   **URL**: `/stops/`
*   **Method**: `GET`
*   **Description**: Retrieves a list of all stops.
*   **Permissions**: `IsAuthenticated`
*   **Success Response (200 OK)**:
    *   Returns a list of `Stop` objects.
    ```json
    [
        {
            "id": 1,
            "name": "City Center",
            "description": "Near the main post office"
        },
        {
            "id": 2,
            "name": "Airport",
            "description": ""
        }
    ]
    ```
---

## Vendor

### Vendor Bookings

*   **URL**: `/vendor-bookings/`
*   **Method**: `GET`
*   **Description**: This is a server-side rendered page that displays all bookings for the trips created by the logged-in vendor. It is not a REST API endpoint.
*   **Permissions**: `login_required`, `vendor_profile`
