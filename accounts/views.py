from django.shortcuts import render, redirect
from .forms import CustomeUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from .models import User, Token
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
import json
from django.urls import reverse
from .utils import send_email, confirm_token


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
        print(user)
        if user is not None:
            print('HEGHJHBHJUHBHJB')
            if not user.is_verified:
                send_email(request, user, mail_subject='Please activate your account', email_template='authentication/account_verification_email.html')
                messages.error(request, 'Account not verified, an activation linked has been sent to your email')
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

def activate(request, token):
    try:
        email = confirm_token(token)
        user = User.objects.get(email=email)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None:
        user.is_verified = True
        user.is_active = True
        user.save()
        token_data = Token.objects.get(email=email, token=token)
        token_data.used = True
        token_data.save()
        messages.success(request, 'Your account is now activated. You can now login')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link!')
        return redirect('login')
    

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            send_email(request, user, mail_subject='Password Reset', email_template='authentication/password_reset_email.html')
            messages.success(request, 'A link has been sent to email.')
            return redirect('password_reset_request')
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            messages.error(request, 'Account with this email does not exist.')
            return redirect('password_reset_request')
    return render(request, 'authentication/password_reset_request.html')

def reset_password(request, token):
    try:
        email = confirm_token(token)
        user = User.objects.get(email=email)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        return redirect('home')
    if request.method == 'POST':
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 != password2:
            messages.error(request, 'Password must match')
            return redirect('reset_password', token)
        user.password = make_password(password1)
        user.save()
        token_data = Token.objects.get(email=email, token=token)
        token_data.used = True
        token_data.save()
        messages.success(request, 'Password has been reset.')
        return redirect('login')
    return render(request, 'authentication/reset_password.html')

def validate_username(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()

            if request.user.is_authenticated:
                if request.user.username == username:
                    return JsonResponse({'success': ''})

            if User.objects.filter(username=username).exists():
                return JsonResponse({'detail': 'Username is taken'}, status=400)

            if ' ' in username:
                return JsonResponse({'detail': 'No spaces'}, status=400)

            return JsonResponse({'success': 'Username is available'})

        except Exception as e:
            return JsonResponse({'detail': 'Invalid request'}, status=400)

    return JsonResponse({'detail': 'Method not allowed'}, status=405)

def validate_user_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_password = data.get('password', '').strip()
            try:
                validate_password(user_password)
                return JsonResponse({'success': 'Password is valid'})
            except ValidationError as e:
                # Return the list of error messages
                return JsonResponse({'detail': e.messages}, status=400)

        except Exception as e:
            return JsonResponse({'detail': 'Invalid request'}, status=400)
    return JsonResponse({'detail': 'Method not allowed'}, status=405)

@login_required(login_url='login')
def delete_account(request):
    user = request.user
    if request.method == 'DELETE':
        user.delete()
        logout(request)
        messages.success(request, 'Account deleted.')
        home_url = reverse('home')
        return JsonResponse({'detail': 'Account deleted.', 'redirect_url': home_url})

@login_required(login_url='login')
def view_account(request):
    if request.method == 'POST':
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            # Save the file to the user's profile
            user = request.user
            user.profile_picture = profile_picture
            user.save()
            messages.success(request, 'Profile picture updated.')
        username = request.POST['username']
        current_password = request.POST.get('current_password', None)
        new_password = request.POST.get('new_password', None)
        new_password2 = request.POST.get('new_password2', None)

        if user.username != username:
            user.username = username
            user.save()
            messages.success(request, 'Username updated')

        if new_password:
            if new_password == new_password2:
                if user.password == make_password(current_password):
                    user.password = make_password(new_password)
                    user.save()
                else:
                    messages.error(request, 'Incorrect password')
            else:
                messages.error(request, 'New Password must match')
        
    return render(request, 'authentication/account.html')
        