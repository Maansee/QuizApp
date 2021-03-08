from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.models import User
import random
from .models import UserOTP
from .import forms
from django.core.mail import send_mail
from django.conf import settings


def register(request):
    if request.method == 'POST':

        #verify otp
        otp_present = request.POST.get('otp')

        if otp_present:
            get_user = request.POST.get('usr')
            usr = User.objects.get(username=get_user)
            if not usr.is_active:
                if int(otp_present)== UserOTP.objects.filter(user = usr).last().otp:
                    usr.is_active = True
                    usr.save()
                    messages.success(request, f'Account created for {usr.username}')
                    return redirect('quiz-home')
                else:
                     messages.error(request, f'Account not created for {usr.username}. Please validate OTP')
                     return render(request, 'user/register.html', {'otp': True, 'usr': usr})



        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            


            usr = User.objects.get(username=username)
            usr.is_active = False
            usr.email = usr.email
            usr.save()   #cannot login until otp is entered

            usr_otp = random.randint(10000, 999999)

            #creating user otp here
            UserOTP.objects.create(user=usr, otp = usr_otp)

            #creating mail msg
            msg = f"Hi {username}, \n Your OTP is {usr_otp}."

            #create an email
            send_mail(
                "Welcome to ExamFunda. Verify your email.",
                msg,
                settings.EMAIL_HOST_USER,
                [usr.email],
                fail_silently = False
                )

            return render(request, 'users/register.html', {'otp':True, 'usr':usr})
            


             
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

