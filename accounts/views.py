from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import logging
logger = logging.getLogger(__name__)
def login_view(request):
    """Widok logowania z Tailwind UI"""
    from django_tenants.utils import schema_context
    logger.debug(f"=== CURRENT SCHEMA: {getattr(request, 'tenant', None)}")
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'🎉 Witaj {user.get_full_name() or user.username}!')
                
                # Redirect do next lub dashboard
                next_url = request.GET.get('next', 'accounts:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, '❌ Nieprawidłowe dane logowania.')
        else:
            messages.error(request, '⚠️ Proszę podać username i hasło.')
    
    context = {
        'tenant': getattr(request, 'tenant', None),
        'next': request.GET.get('next', ''),
    }
    return render(request, 'accounts/login.html', context)

def logout_view(request):
    """Widok wylogowania"""
    if request.user.is_authenticated:
        username = request.user.get_full_name() or request.user.username
        logout(request)
        messages.info(request, f'👋 Do zobaczenia {username}!')
    return redirect('accounts:login')

@login_required
def dashboard_view(request):
    """Dashboard użytkownika z Tailwind UI"""
    context = {
        'user': request.user,
        'tenant': getattr(request, 'tenant', None),
    }
    return render(request, 'accounts/dashboard.html', context)

@require_http_methods(["GET"])
def tenant_info_api(request):
    """API endpoint z informacją o tenancie"""
    tenant = getattr(request, 'tenant', None)
    if tenant:
        return JsonResponse({
            'tenant_name': tenant.name,
            'schema_name': tenant.schema_name,
            'user_authenticated': request.user.is_authenticated,
            'username': request.user.username if request.user.is_authenticated else None,
            'user_full_name': request.user.get_full_name() if request.user.is_authenticated else None,
        })
    return JsonResponse({'error': 'No tenant found'}, status=404)

def home_view(request):
    """Strona główna - redirect do dashboard lub login"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return redirect('accounts:login')