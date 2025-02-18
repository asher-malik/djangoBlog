from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomeUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password
from .models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from .utils import send_email


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomeUserCreationForm(request.POST)
        email = request.POST['email']
        username = request.POST['username']
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Account already exists login instead')
            return redirect('login')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username has been taken')
            return redirect('register')
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            hashed_password = make_password(password)
            user = User.objects.create(username=username, email=email, password=hashed_password)
            user.save()
            send_email(request, user, mail_subject='Account Verification', email_template='authentication/account_verification_email.html')
            messages.success(request, 'An activation link has been sent to your email')        
            return redirect('login')
        else:
            # Handle form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
                return redirect('register')
            try:
                validate_password(request.POST['password1'])
            except ValidationError as e:
                for error in e:
                    messages.error(request, error)
                return redirect('register')
        
    form = CustomeUserCreationForm()
    context = {
            'form': form,
        }
    return render(request, 'authentication/register.html', context)

def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if not user.is_verified:
                send_email(request, user, mail_subject='Please activate your account', email_template='accounts/account_verification_email.html')
                messages.error(request, 'Account not verified, an activation linked has been sent to your email')
                return redirect('login')
            if not user.is_active:
                messages.error(request, 'Your account is not activated')
                return redirect('login')
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    return render(request, 'authentication/login.html')

@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_verified = True
        user.is_active = True
        user.save()
        messages.success(request, 'Your account is now activated. You can now login')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link!')
        return redirect('login')