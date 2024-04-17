from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from LoginRe import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes 
from .token import generate_token
from django.core.mail import EmailMessage
def home(request):
    return render(request, "authentication/index.html")

def signup(request):
    
    if request.method == "POST":
        username = request.POST['username']
        Fname = request.POST['fname']
        Lname = request.POST['lname']
        Email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username") 
            return redirect('home')
        
        if User.objects.filter(email=Email):
            messages.error(request, "Email already exist! ") 
            return redirect('home')
        
        if len(username)>10:
            messages.error(request, "Username must be under 10 characters")
        if pass1 != pass2:
            messages.error(request, "Passwords didn't match!")
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!")
            return redirect('home')
        
        myuser = User.objects.create_user(username, Email, pass1)
        myuser.first_name = Fname
        myuser.last_name = Lname
        myuser.is_active = False
        myuser.save()
        messages.success(request, """we have sent you a confirmation email.
                         You have to activate your account.""")
        
        
        #Sending Email 
        subject = "This is for Confirmation"
        message = "Hello, \n"+ "Greetings from Khedeji_Ka_Blog \n"+ "You have Successfully Registered as a user \n" + "Thank you"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message,  from_email, to_list ,fail_silently=True)
        
     
        #Email Confirmation
        current_site = get_current_site(request)
        email_subject = "Confirm your email  Login!!" 
        message2 = render_to_string('email_confirmation.html',{
                    'name': myuser.first_name,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
                    'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        return redirect("signin")
    
    
    
    return render(request, 'authentication/signup.html')

def signin(request):
    
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, 'authentication/index.html', {'fname':fname,})
        else:
            messages.error(request,"Bad Credential")
            return redirect('home')
    
    
    return render(request, 'authentication/signin.html')

def signout(request):
    logout(request)
    messages.success(request, "Logout Successfully")
    return redirect('home')

def activate (request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist): 
        myuser = None
    if myuser is not None and generate_token.check_token (myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        fname = myuser.first_name
        return render(request, 'authentication/index.html', {'fname':fname,})
    else:
        return render (request, 'activation_failed.html')