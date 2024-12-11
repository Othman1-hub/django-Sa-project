from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .forms import CustomUserCreationForm, EventForm, TicketForm, FeedbackForm
from .models import Event, Ticket, Feedback
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import LoginView
from django.db import models

class CustomLoginView(LoginView):
    template_name = 'login.html'

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def home(request):
    if request.user.is_organizer:
        events = Event.objects.filter(organizer=request.user)
        return render(request, 'organizer_home.html', {'events': events})
    else:
        events = Event.objects.all().order_by('date')
        paginator = Paginator(events, 10)  # Show 10 events per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'attendee_home.html', {'events': page_obj})

@login_required
def create_event(request):
    if not request.user.is_organizer:
        messages.error(request, 'You do not have permission to create events.')
        return redirect('home')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('home')
    else:
        form = EventForm()
    return render(request, 'create_event.html', {'form': form})

@login_required
def buy_ticket(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.event = event
            ticket.user = request.user
            ticket.save()
            messages.success(request, 'Ticket purchased successfully!')
            send_mail(
                'Ticket Confirmation',
                f'Your ticket for {event.name} has been confirmed.',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
            return redirect('my_tickets')
    else:
        form = TicketForm()
    return render(request, 'buy_ticket.html', {'form': form, 'event': event})

@login_required
def submit_feedback(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.event = ticket.event
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('my_tickets')
    else:
        form = FeedbackForm()
    return render(request, 'submit_feedback.html', {'form': form, 'ticket': ticket})

@login_required
def generate_report(request):
    if not request.user.is_organizer:
        messages.error(request, 'You do not have permission to access reports.')
        return redirect('home')

    events = Event.objects.filter(organizer=request.user)
    report_data = []
    for event in events:
        tickets_sold = Ticket.objects.filter(event=event).count()
        feedback = Feedback.objects.filter(event=event)
        avg_rating = feedback.aggregate(models.Avg('rating'))['rating__avg']
        report_data.append({
            'event': event,
            'tickets_sold': tickets_sold,
            'avg_rating': avg_rating
        })
    return render(request, 'report.html', {'report_data': report_data})

@login_required
def event_details(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'event_details.html', {'event': event})

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user != event.organizer:
        messages.error(request, 'You do not have permission to edit this event.')
        return redirect('event_details', event_id=event.id)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_details', event_id=event.id)
    else:
        form = EventForm(instance=event)
    
    return render(request, 'edit_event.html', {'form': form, 'event': event})

@login_required
def events_list(request):
    events = Event.objects.all().order_by('date')
    paginator = Paginator(events, 10)  # Show 10 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'events_list.html', {'events': page_obj})

@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user).order_by('-purchase_date')
    return render(request, 'my_tickets.html', {'tickets': tickets})

def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

