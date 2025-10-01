# Building an Uber-like App with FlashFlow

This guide walks you through building a ride-sharing application similar to Uber using FlashFlow's single-syntax approach. You'll learn how to implement all the core features needed for a complete ride-sharing platform.

## Table of Contents

1. [Overview](#overview)
2. [Core Features](#core-features)
3. [Project Setup](#project-setup)
4. [Data Models](#data-models)
5. [User Authentication](#user-authentication)
6. [Location Services](#location-services)
7. [Ride Management](#ride-management)
8. [Payment Processing](#payment-processing)
9. [Real-time Communication](#real-time-communication)
10. [Notifications](#notifications)
11. [Admin Panel](#admin-panel)
12. [Mobile App Features](#mobile-app-features)
13. [Testing](#testing)
14. [Deployment](#deployment)

## Overview

An Uber-like application requires several key components working together:
- User registration and authentication
- Real-time location tracking
- Ride request and matching system
- Payment processing
- Driver and passenger communication
- Notifications and alerts
- Admin dashboard for monitoring

With FlashFlow, you can implement all these features using a single `.flow` syntax that generates complete backend, frontend, and mobile applications.

## Core Features

The app will include these essential features:

### For Passengers
- User registration and login
- Location services (pickup/dropoff points)
- Ride request and tracking
- Real-time driver location
- Payment processing
- Ride history
- Ratings and reviews

### For Drivers
- Driver registration and verification
- Availability status management
- Ride request notifications
- Navigation to pickup/dropoff
- Earnings tracking
- Rating system

### For Admins
- User and driver management
- Ride monitoring
- Payment reconciliation
- Analytics dashboard
- Support ticket system

## Project Setup

### Initialize the Project

Create a new FlashFlow project:

```bash
flashflow new ride-sharing-app
cd ride-sharing-app
```

### Configure Project Settings

Update your `flashflow.json`:

```json
{
  "name": "ride-sharing-app",
  "version": "1.0.0",
  "description": "Uber-like ride sharing application",
  "author": "Your Name",
  "frameworks": {
    "backend": "laravel",
    "frontend": "react",
    "mobile": "flet",
    "database": "postgresql"
  },
  "dependencies": [
    "stripe",
    "firebase",
    "google-maps"
  ]
}
```

### Install Dependencies

```bash
flashflow install core
flashflow install google-maps --save
flashflow install stripe --save
```

## Data Models

### User Model

```yaml
model:
  name: "User"
  fields:
    - name: "id"
      type: "uuid"
      primary: true
    - name: "email"
      type: "string"
      required: true
      unique: true
    - name: "phone"
      type: "string"
      required: true
      unique: true
    - name: "first_name"
      type: "string"
      required: true
    - name: "last_name"
      type: "string"
      required: true
    - name: "profile_picture"
      type: "url"
    - name: "user_type"
      type: "enum"
      values: ["passenger", "driver", "admin"]
      default: "passenger"
    - name: "is_verified"
      type: "boolean"
      default: false
    - name: "rating"
      type: "decimal"
      precision: 3
      scale: 2
      default: 0.00
    - name: "total_rides"
      type: "integer"
      default: 0
    - name: "created_at"
      type: "timestamp"
      auto: true
    - name: "updated_at"
      type: "timestamp"
      auto: true
```

### Driver Model

```yaml
model:
  name: "Driver"
  fields:
    - name: "id"
      type: "uuid"
      primary: true
    - name: "user_id"
      type: "foreign_key"
      references: "users.id"
      required: true
      unique: true
    - name: "license_number"
      type: "string"
      required: true
      unique: true
    - name: "vehicle_make"
      type: "string"
      required: true
    - name: "vehicle_model"
      type: "string"
      required: true
    - name: "vehicle_year"
      type: "integer"
      required: true
    - name: "vehicle_color"
      type: "string"
      required: true
    - name: "vehicle_plate"
      type: "string"
      required: true
    - name: "vehicle_capacity"
      type: "integer"
      default: 4
    - name: "is_active"
      type: "boolean"
      default: false
    - name: "is_available"
      type: "boolean"
      default: true
    - name: "current_location"
      type: "json"  # {lat, lng}
    - name: "last_seen"
      type: "timestamp"
    - name: "total_earnings"
      type: "decimal"
      precision: 10
      scale: 2
      default: 0.00
    - name: "created_at"
      type: "timestamp"
      auto: true
    - name: "updated_at"
      type: "timestamp"
      auto: true
  relationships:
    - name: "user"
      type: "belongsTo"
      model: "User"
    - name: "rides"
      type: "hasMany"
      model: "Ride"
```

### Ride Model

```yaml
model:
  name: "Ride"
  fields:
    - name: "id"
      type: "uuid"
      primary: true
    - name: "passenger_id"
      type: "foreign_key"
      references: "users.id"
      required: true
    - name: "driver_id"
      type: "foreign_key"
      references: "drivers.id"
      nullable: true
    - name: "pickup_location"
      type: "json"  # {lat, lng, address}
      required: true
    - name: "dropoff_location"
      type: "json"  # {lat, lng, address}
      required: true
    - name: "pickup_time"
      type: "timestamp"
    - name: "dropoff_time"
      type: "timestamp"
    - name: "status"
      type: "enum"
      values: ["requested", "accepted", "arrived", "started", "completed", "cancelled", "rejected"]
      default: "requested"
    - name: "estimated_fare"
      type: "decimal"
      precision: 10
      scale: 2
    - name: "actual_fare"
      type: "decimal"
      precision: 10
      scale: 2
    - name: "distance"
      type: "decimal"
      precision: 8
      scale: 2  # in kilometers
    - name: "duration"
      type: "integer"  # in minutes
    - name: "payment_method"
      type: "string"
    - name: "payment_status"
      type: "enum"
      values: ["pending", "completed", "failed", "refunded"]
      default: "pending"
    - name: "rating"
      type: "integer"  # 1-5 stars
    - name: "review"
      type: "text"
    - name: "cancelled_by"
      type: "enum"
      values: ["passenger", "driver", "system"]
    - name: "cancellation_reason"
      type: "string"
    - name: "created_at"
      type: "timestamp"
      auto: true
    - name: "updated_at"
      type: "timestamp"
      auto: true
  relationships:
    - name: "passenger"
      type: "belongsTo"
      model: "User"
    - name: "driver"
      type: "belongsTo"
      model: "Driver"
    - name: "payments"
      type: "hasMany"
      model: "Payment"
```

### Payment Model

```yaml
model:
  name: "Payment"
  fields:
    - name: "id"
      type: "uuid"
      primary: true
    - name: "ride_id"
      type: "foreign_key"
      references: "rides.id"
      required: true
    - name: "amount"
      type: "decimal"
      precision: 10
      scale: 2
      required: true
    - name: "currency"
      type: "string"
      default: "USD"
    - name: "payment_method"
      type: "string"  # stripe, paypal, cash, etc.
    - name: "payment_intent_id"
      type: "string"  # for Stripe
    - name: "status"
      type: "enum"
      values: ["pending", "processing", "completed", "failed", "refunded"]
      default: "pending"
    - name: "processed_at"
      type: "timestamp"
    - name: "created_at"
      type: "timestamp"
      auto: true
  relationships:
    - name: "ride"
      type: "belongsTo"
      model: "Ride"
```

## User Authentication

### Authentication Configuration

```yaml
authentication:
  providers:
    - name: "local"
      type: "email_password"
    - name: "google"
      type: "oauth2"
      client_id: "{{ env.GOOGLE_CLIENT_ID }}"
    - name: "facebook"
      type: "oauth2"
      client_id: "{{ env.FACEBOOK_APP_ID }}"
  jwt:
    secret: "{{ env.JWT_SECRET }}"
    expiration: "24h"
  verification:
    email: true
    phone: true
  roles:
    - name: "passenger"
      default: true
    - name: "driver"
    - name: "admin"
```

### Registration Pages

```yaml
page:
  title: "Sign Up as Passenger"
  path: "/register/passenger"
  body:
    - component: "form"
      action: "register_passenger"
      fields:
        - name: "email"
          type: "email"
          required: true
          placeholder: "Enter your email"
        - name: "phone"
          type: "phone"
          required: true
          placeholder: "Enter your phone number"
        - name: "password"
          type: "password"
          required: true
          placeholder: "Create a password"
        - name: "first_name"
          type: "text"
          required: true
          placeholder: "First name"
        - name: "last_name"
          type: "text"
          required: true
          placeholder: "Last name"
      submit_text: "Create Account"
      redirect_on_success: "/verify-phone"

page:
  title: "Sign Up as Driver"
  path: "/register/driver"
  body:
    - component: "form"
      action: "register_driver"
      fields:
        - name: "email"
          type: "email"
          required: true
          placeholder: "Enter your email"
        - name: "phone"
          type: "phone"
          required: true
          placeholder: "Enter your phone number"
        - name: "password"
          type: "password"
          required: true
          placeholder: "Create a password"
        - name: "first_name"
          type: "text"
          required: true
          placeholder: "First name"
        - name: "last_name"
          type: "text"
          required: true
          placeholder: "Last name"
        - name: "license_number"
          type: "text"
          required: true
          placeholder: "Driver's license number"
        - name: "vehicle_make"
          type: "text"
          required: true
          placeholder: "Vehicle make"
        - name: "vehicle_model"
          type: "text"
          required: true
          placeholder: "Vehicle model"
        - name: "vehicle_year"
          type: "number"
          required: true
          placeholder: "Vehicle year"
        - name: "vehicle_color"
          type: "text"
          required: true
          placeholder: "Vehicle color"
        - name: "vehicle_plate"
          type: "text"
          required: true
          placeholder: "License plate number"
      submit_text: "Apply to Drive"
      redirect_on_success: "/driver-application-submitted"
```

## Location Services

### Location Model

```yaml
model:
  name: "Location"
  fields:
    - name: "id"
      type: "uuid"
      primary: true
    - name: "user_id"
      type: "foreign_key"
      references: "users.id"
    - name: "latitude"
      type: "decimal"
      precision: 10
      scale: 8
      required: true
    - name: "longitude"
      type: "decimal"
      precision: 11
      scale: 8
      required: true
    - name: "address"
      type: "string"
    - name: "location_type"
      type: "enum"
      values: ["current", "pickup", "dropoff", "favorite"]
    - name: "created_at"
      type: "timestamp"
      auto: true
```

### Location API Endpoints

```yaml
endpoint:
  path: "/api/locations/current"
  method: "POST"
  auth: "jwt"
  description: "Update user's current location"
  request:
    latitude:
      type: "number"
      required: true
    longitude:
      type: "number"
      required: true
  response:
    status:
      type: "string"
    message:
      type: "string"

endpoint:
  path: "/api/locations/nearby-drivers"
  method: "GET"
  auth: "jwt"
  description: "Get nearby available drivers"
  query_params:
    latitude:
      type: "number"
      required: true
    longitude:
      type: "number"
      required: true
    radius:
      type: "number"
      default: 5000  # meters
  response:
    drivers:
      type: "array"
      items:
        type: "object"
        properties:
          id:
            type: "string"
          latitude:
            type: "number"
          longitude:
            type: "number"
          driver_name:
            type: "string"
          vehicle:
            type: "string"
          rating:
            type: "number"
          eta:
            type: "number"  # minutes
```

## Ride Management

### Ride Request Flow

```yaml
# Passenger requests a ride
endpoint:
  path: "/api/rides/request"
  method: "POST"
  auth: "jwt"
  description: "Request a new ride"
  request:
    pickup_location:
      type: "object"
      required: true
      properties:
        lat:
          type: "number"
        lng:
          type: "number"
        address:
          type: "string"
    dropoff_location:
      type: "object"
      required: true
      properties:
        lat:
          type: "number"
        lng:
          type: "number"
        address:
          type: "string"
  response:
    ride_id:
      type: "string"
    status:
      type: "string"
    message:
      type: "string"

# Driver accepts a ride
endpoint:
  path: "/api/rides/{ride_id}/accept"
  method: "POST"
  auth: "jwt"
  description: "Driver accepts a ride request"
  request:
    driver_id:
      type: "string"
      required: true
  response:
    status:
      type: "string"
    message:
      type: "string"

# Update ride status
endpoint:
  path: "/api/rides/{ride_id}/status"
  method: "PUT"
  auth: "jwt"
  description: "Update ride status"
  request:
    status:
      type: "string"
      enum: ["accepted", "arrived", "started", "completed", "cancelled"]
      required: true
    location:
      type: "object"
      properties:
        lat:
          type: "number"
        lng:
          type: "number"
  response:
    status:
      type: "string"
    message:
      type: "string"
```

### Ride Tracking Pages

```yaml
page:
  title: "Request Ride"
  path: "/ride/request"
  auth: true
  body:
    - component: "map"
      id: "ride-request-map"
      height: "400px"
      center:
        lat: "{{ user.current_location.lat }}"
        lng: "{{ user.current_location.lng }}"
      zoom: 15
      markers:
        - position:
            lat: "{{ user.current_location.lat }}"
            lng: "{{ user.current_location.lng }}"
          icon: "user"
          draggable: true
          on_drag_end: "update_pickup_location"
      controls:
        - type: "search_box"
          placeholder: "Where to?"
          on_search: "set_dropoff_location"
        - type: "locate_me"
          on_click: "center_on_user_location"
    - component: "ride_request_form"
      on_submit: "request_ride"
      submit_text: "Request Ride"

page:
  title: "Ride Tracking"
  path: "/ride/{ride_id}"
  auth: true
  body:
    - component: "map"
      id: "ride-tracking-map"
      height: "400px"
      center:
        lat: "{{ ride.pickup_location.lat }}"
        lng: "{{ ride.pickup_location.lng }}"
      zoom: 13
      markers:
        - position: "{{ ride.pickup_location }}"
          icon: "pickup"
          label: "Pickup"
        - position: "{{ ride.dropoff_location }}"
          icon: "dropoff"
          label: "Dropoff"
        - position: "{{ ride.driver.current_location }}"
          icon: "car"
          label: "{{ ride.driver.name }}"
          rotation: "{{ ride.driver.heading }}"
      polylines:
        - path: "{{ ride.route }}"
          color: "#3B82F6"
          stroke_weight: 4
      live_updates: true
    - component: "ride_status_panel"
      ride: "{{ ride }}"
      on_cancel: "cancel_ride"
```

## Payment Processing

### Payment Integration

```yaml
payments:
  providers: ["stripe"]
  default_provider: "stripe"
  currency: "USD"
  stripe:
    public_key: "{{ env.STRIPE_PUBLIC_KEY }}"
    secret_key: "{{ env.STRIPE_SECRET_KEY }}"
    webhook_secret: "{{ env.STRIPE_WEBHOOK_SECRET }}"
    supported_methods: ["card", "apple_pay", "google_pay"]

# Payment API endpoints
endpoint:
  path: "/api/payments/intent"
  method: "POST"
  auth: "jwt"
  description: "Create payment intent for ride"
  request:
    ride_id:
      type: "string"
      required: true
    amount:
      type: "number"
      required: true
  response:
    client_secret:
      type: "string"
    payment_id:
      type: "string"

endpoint:
  path: "/api/payments/confirm"
  method: "POST"
  auth: "jwt"
  description: "Confirm payment completion"
  request:
    payment_id:
      type: "string"
      required: true
    ride_id:
      type: "string"
      required: true
  response:
    status:
      type: "string"
    message:
      type: "string"
```

### Payment Pages

```yaml
page:
  title: "Payment"
  path: "/ride/{ride_id}/payment"
  auth: true
  body:
    - component: "payment_summary"
      ride: "{{ ride }}"
      show_fare_breakdown: true
      show_driver_info: true
    - component: "payment_form"
      providers: ["stripe"]
      save_payment_method: true
      on_submit: "process_payment"
      submit_text: "Pay {{ ride.estimated_fare }}"
    - component: "payment_methods"
      saved_methods: "{{ user.payment_methods }}"
      on_select: "use_saved_payment_method"
```

## Real-time Communication

### Chat Integration

```yaml
# Real-time chat for driver-passenger communication
websocket:
  connection: "ride_chat"
  path: "/ws/rides/{ride_id}/chat"
  authentication: required
  max_connections: 2  # Only driver and passenger

events:
  message_sent:
    trigger: "user_sends_message"
    broadcast: "ride_participants"
    data:
      - user_id
      - user_name
      - message_content
      - timestamp

  ride_status_updated:
    trigger: "ride_status_changes"
    broadcast: "ride_participants"
    data:
      - ride_id
      - status
      - location

streams:
  ride_updates:
    type: "real_time"
    source: "rides_table"
    filter:
      - id: "{{ ride_id }}"
    on_change: "broadcast_ride_update"

  chat_messages:
    type: "real_time"
    source: "messages_table"
    filter:
      - ride_id: "{{ ride_id }}"
    order_by: "created_at ASC"
```

### Communication Pages

```yaml
page:
  title: "Ride Chat"
  path: "/ride/{ride_id}/chat"
  auth: true
  body:
    - component: "chat_window"
      ride_id: "{{ ride_id }}"
      messages: "{{ chat_messages }}"
      on_send: "send_message"
      on_typing: "send_typing_indicator"
    - component: "ride_status_updates"
      ride: "{{ ride }}"
      live_updates: true
```

## Notifications

### Push Notification Configuration

```yaml
push_notifications:
  providers: ["firebase"]
  default_provider: "firebase"
  firebase:
    project_id: "{{ env.FIREBASE_PROJECT_ID }}"
    private_key: "{{ env.FIREBASE_PRIVATE_KEY }}"
    client_email: "{{ env.FIREBASE_CLIENT_EMAIL }}"
    server_key: "{{ env.FIREBASE_SERVER_KEY }}"

# Notification templates
notification_templates:
  - name: "ride_requested"
    title: "New Ride Request"
    body: "A passenger has requested a ride near you. Pickup: {{ pickup_address }}"
    category: "ride"
    action_buttons:
      - text: "Accept"
        action: "accept_ride"
        data:
          ride_id: "{{ ride_id }}"
      - text: "Decline"
        action: "decline_ride"
        data:
          ride_id: "{{ ride_id }}"

  - name: "ride_accepted"
    title: "Driver Accepted Your Ride"
    body: "{{ driver_name }} is on the way to pick you up. ETA: {{ eta }} minutes."
    category: "ride"

  - name: "driver_arrived"
    title: "Driver Arrived"
    body: "{{ driver_name }} has arrived at your pickup location."
    category: "ride"

  - name: "ride_started"
    title: "Ride Started"
    body: "Your ride with {{ driver_name }} has started."
    category: "ride"

  - name: "ride_completed"
    title: "Ride Completed"
    body: "Your ride is complete. Please rate your experience."
    category: "ride"
    action_buttons:
      - text: "Rate Ride"
        action: "rate_ride"
        data:
          ride_id: "{{ ride_id }}"
```

### Notification API Endpoints

```yaml
endpoint:
  path: "/api/notifications/device-token"
  method: "POST"
  auth: "jwt"
  description: "Register device token for push notifications"
  request:
    device_token:
      type: "string"
      required: true
    platform:
      type: "string"
      enum: ["android", "ios", "web"]
      required: true
  response:
    status:
      type: "string"
    message:
      type: "string"
```

## Admin Panel

### Admin Dashboard

```yaml
page:
  title: "Admin Dashboard"
  path: "/admin"
  auth: true
  roles: ["admin"]
  body:
    - component: "admin_header"
      title: "Ride Sharing Admin Panel"
    - component: "stats_cards"
      cards:
        - title: "Active Rides"
          value: "{{ active_rides_count }}"
          icon: "car"
          color: "blue"
        - title: "Online Drivers"
          value: "{{ online_drivers_count }}"
          icon: "driver"
          color: "green"
        - title: "Today's Revenue"
          value: "{{ todays_revenue }}"
          icon: "revenue"
          color: "purple"
        - title: "Pending Drivers"
          value: "{{ pending_drivers_count }}"
          icon: "user-check"
          color: "orange"
    - component: "real_time_map"
      height: "500px"
      markers:
        - position:
            lat: "{{ driver.location.lat }}"
            lng: "{{ driver.location.lng }}"
          icon: "driver"
          label: "{{ driver.name }}"
          popup: "{{ driver.vehicle }} - Rating: {{ driver.rating }}"
        - position:
            lat: "{{ active_ride.pickup.lat }}"
            lng: "{{ active_ride.pickup.lng }}"
          icon: "pickup"
          label: "Pickup"
        - position:
            lat: "{{ active_ride.dropoff.lat }}"
            lng: "{{ active_ride.dropoff.lng }}"
          icon: "dropoff"
          label: "Dropoff"
      live_updates: true
    - component: "recent_activities"
      activities: "{{ recent_activities }}"
      limit: 10

# Admin API endpoints
endpoint:
  path: "/api/admin/drivers"
  method: "GET"
  auth: "jwt"
  roles: ["admin"]
  description: "Get list of all drivers"
  query_params:
    status:
      type: "string"
      enum: ["pending", "active", "inactive"]
    page:
      type: "number"
      default: 1
    limit:
      type: "number"
      default: 20
  response:
    drivers:
      type: "array"
      items: "Driver"
    pagination:
      type: "object"

endpoint:
  path: "/api/admin/drivers/{driver_id}/approve"
  method: "POST"
  auth: "jwt"
  roles: ["admin"]
  description: "Approve driver application"
  response:
    status:
      type: "string"
    message:
      type: "string"

endpoint:
  path: "/api/admin/drivers/{driver_id}/suspend"
  method: "POST"
  auth: "jwt"
  roles: ["admin"]
  description: "Suspend driver account"
  request:
    reason:
      type: "string"
      required: true
  response:
    status:
      type: "string"
    message:
      type: "string"
```

## Mobile App Features

### Mobile-Specific Components

```yaml
# Mobile app pages
page:
  title: "Driver Dashboard"
  path: "/driver/dashboard"
  auth: true
  roles: ["driver"]
  layout: "mobile"
  body:
    - component: "driver_status_toggle"
      is_available: "{{ driver.is_available }}"
      on_toggle: "toggle_driver_status"
    - component: "earnings_summary"
      today_earnings: "{{ driver.today_earnings }}"
      weekly_earnings: "{{ driver.weekly_earnings }}"
      rating: "{{ driver.rating }}"
    - component: "active_rides_list"
      rides: "{{ driver.active_rides }}"
    - component: "nearby_requests_map"
      height: "300px"
      center:
        lat: "{{ driver.location.lat }}"
        lng: "{{ driver.location.lng }}"
      nearby_rides: "{{ nearby_ride_requests }}"
      on_accept: "accept_ride"

page:
  title: "Passenger Home"
  path: "/passenger/home"
  auth: true
  roles: ["passenger"]
  layout: "mobile"
  body:
    - component: "location_search"
      current_location: "{{ user.current_location }}"
      on_search: "search_location"
      on_select: "select_location"
    - component: "quick_destinations"
      favorites: "{{ user.favorite_locations }}"
      on_select: "set_destination"
    - component: "ride_estimate"
      pickup: "{{ user.current_location }}"
      destination: "{{ selected_destination }}"
      on_request: "request_ride"
    - component: "active_ride_card"
      ride: "{{ user.active_ride }}"
      on_track: "track_ride"
      on_chat: "open_chat"

# Mobile-specific API endpoints
endpoint:
  path: "/api/mobile/location"
  method: "POST"
  auth: "jwt"
  description: "Update mobile user location"
  request:
    latitude:
      type: "number"
      required: true
    longitude:
      type: "number"
      required: true
    heading:
      type: "number"
    speed:
      type: "number"
  response:
    status:
      type: "string"

endpoint:
  path: "/api/mobile/ride/{ride_id}/navigate"
  method: "POST"
  auth: "jwt"
  description: "Get navigation instructions for ride"
  response:
    route:
      type: "object"
    instructions:
      type: "array"
    estimated_time:
      type: "number"
```

## Testing

### Test Flows

```yaml
# User registration test
test:
  name: "Passenger Registration"
  description: "Test passenger registration flow"
  steps:
    - action: "visit"
      url: "/register/passenger"
    - action: "fill"
      field: "email"
      value: "test@example.com"
    - action: "fill"
      field: "phone"
      value: "+1234567890"
    - action: "fill"
      field: "password"
      value: "SecurePass123!"
    - action: "fill"
      field: "first_name"
      value: "John"
    - action: "fill"
      field: "last_name"
      value: "Doe"
    - action: "click"
      element: "submit_button"
    - action: "assert"
      condition: "redirected_to"
      value: "/verify-phone"

# Ride request test
test:
  name: "Ride Request Flow"
  description: "Test complete ride request and acceptance flow"
  steps:
    - action: "login"
      credentials:
        email: "passenger@example.com"
        password: "SecurePass123!"
    - action: "visit"
      url: "/ride/request"
    - action: "set_location"
      type: "pickup"
      lat: 40.7128
      lng: -74.0060
    - action: "set_location"
      type: "dropoff"
      lat: 40.7589
      lng: -73.9851
    - action: "click"
      element: "request_ride_button"
    - action: "assert"
      condition: "ride_status"
      value: "requested"
    - action: "login"
      credentials:
        email: "driver@example.com"
        password: "DriverPass123!"
    - action: "accept_ride"
      ride_id: "{{ last_ride_id }}"
    - action: "assert"
      condition: "ride_status"
      value: "accepted"

# Payment processing test
test:
  name: "Payment Processing"
  description: "Test payment processing flow"
  steps:
    - action: "login"
      credentials:
        email: "passenger@example.com"
        password: "SecurePass123!"
    - action: "visit"
      url: "/ride/{{ ride_id }}/payment"
    - action: "fill"
      field: "card_number"
      value: "4242424242424242"
    - action: "fill"
      field: "expiry"
      value: "12/25"
    - action: "fill"
      field: "cvc"
      value: "123"
    - action: "click"
      element: "pay_button"
    - action: "assert"
      condition: "payment_status"
      value: "completed"
```

## Deployment

### Environment Configuration

```bash
# Create environment file
echo "STRIPE_PUBLIC_KEY=your_stripe_public_key" > .env
echo "STRIPE_SECRET_KEY=your_stripe_secret_key" >> .env
echo "FIREBASE_PROJECT_ID=your_firebase_project_id" >> .env
echo "GOOGLE_MAPS_API_KEY=your_google_maps_api_key" >> .env
```

### Build and Deploy

```bash
# Build the application
flashflow build --production

# Deploy backend
flashflow deploy --platform backend --env production

# Deploy frontend
flashflow deploy --platform frontend --env production

# Deploy mobile apps
flashflow deploy --platform mobile --env production
```

### Monitoring and Analytics

```yaml
# Analytics configuration
analytics:
  providers: ["google_analytics", "mixpanel"]
  google_analytics:
    tracking_id: "{{ env.GA_TRACKING_ID }}"
  mixpanel:
    token: "{{ env.MIXPANEL_TOKEN }}"

  events:
    - name: "ride_requested"
      description: "User requested a ride"
      properties: ["user_id", "pickup_location", "dropoff_location"]
    - name: "ride_completed"
      description: "Ride was completed successfully"
      properties: ["ride_id", "duration", "distance", "fare"]
    - name: "driver_registered"
      description: "New driver registered"
      properties: ["driver_id", "vehicle_type"]

# Error tracking
error_tracking:
  provider: "sentry"
  dsn: "{{ env.SENTRY_DSN }}"
  environment: "{{ env.APP_ENV }}"
```

## Conclusion

With FlashFlow, you can build a complete Uber-like ride-sharing application using a single syntax that generates all the necessary code for backend, frontend, and mobile platforms. The framework handles the complexity of real-time communication, payment processing, location services, and user authentication, allowing you to focus on building great user experiences.

The key advantages of using FlashFlow for this project include:
- **Single codebase**: Write once, deploy everywhere
- **Real-time features**: Built-in WebSocket support for live updates
- **Payment integration**: Pre-built payment processing with Stripe
- **Push notifications**: Complete notification system with Firebase
- **Mobile-first**: Native mobile app generation with Flet
- **Admin panel**: Automatic admin interface generation
- **Testing framework**: Built-in testing capabilities

To get started, create a new FlashFlow project and begin implementing the data models and pages described in this guide. The framework