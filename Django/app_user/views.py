from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from app_core import daos

from app_core.daos import *
from app_core.models import ACCOUNT
from .forms import CustomUserCreationForm, CustomUserFindForm, CustomPasswordResetForm


# 메인 페이지
def user_index(request):

    # 검색어
    search = request.GET.get('search', '')

    account = daos.get_account(request.user.username)
    if request.user.is_superuser:
        places = daos.search_places(search, ['active', 'writing'])
    else:
        places = daos.search_places(search, ['active'])

    return render(request, 'index.html', {
        'places': places,
        'search': search,
        'account': account,
    })

# 로그인 페이지
def user_login(request):
    signup_success = request.session.get('signup_success', False)
    password_reset_success = request.session.get('password_reset_success', False)

    if request.method == 'POST': # 로그인 시도
        form = AuthenticationForm(request, data=request.POST)

        form.error_messages = {
            'invalid_login': _(
                'Invalid username or password. Please enter a correct username and password.'
            ),
            'inactive': _('This account is inactive.'),
        }

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect('user_index')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {
        'form': form,
        'signup_success': signup_success,
        'password_reset_success': password_reset_success,
    })

# 로그아웃
def user_logout(request):
    logout(request)
    return redirect('user_login')

# 회원가입 페이지
def user_signup(request):

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            request.session['signup_success'] = True

            print("회원가입 성공")

            return redirect('user_login')
        else:
            print("회원가입 실패")

    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})

# 계정 찾기 페이지
def user_find(request):
    form = CustomUserFindForm(request.POST or None)
    context = {
        'form': form
    }

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        user_exist = find_account(username)

        context = {
            'form': form,
            'user_exist': user_exist,
        }

        if user_exist:
            request.session['reset_username'] = username

            return redirect('user_reset')

    return render(request, 'find.html', context)

# 비밀번호 초기화 페이지
def user_reset(request):
    username = request.session.get('reset_username')

    if not username:
        return redirect('user_find')

    user = get_object_or_404(ACCOUNT, username=username)

    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)

        if form.is_valid():
            new_password = form.cleaned_data.get("password1")

            user.set_password(new_password)

            user.save()

            request.session.pop('reset_username', None)
            request.session['password_reset_success'] = True

            return redirect('user_login')
    else:
        form = CustomPasswordResetForm()

    return render(request, 'reset.html', {'form': form})

# 프로필
@login_required
def user_profile(request):
    account = daos.get_account(request.user.username)

    return render(request, 'profile.html' , {
        'account': account,
    })

@login_required
@require_http_methods(["POST"])
def user_delete(request):
    user = request.user

    user.delete()
    logout(request)

    messages.success(request, "Account deleted successfully.")

    return redirect('home')  # 메인 페이지 또는 원하는 페이지로 리다이렉트

# 이용약관
def user_terms(request):
    return render(request, 'terms.html')

# 연락처
def user_contact(request):
    return render(request, 'contact.html')