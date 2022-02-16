from django.shortcuts import render, HttpResponse, redirect
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from pymongo import MongoClient
from email import message
from authentication.models import Contact
from email.policy import HTTP
from lib2to3.pgen2.tokenize import generate_tokens
import re
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from gfg import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode 
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.core.mail import EmailMessage, send_mail
from django.utils.http import urlsafe_base64_decode
from neo4j import GraphDatabase
import pandas
import numpy



# Create your views here.
def index(request):
    context = {
        "variable1":"Knowledge Platform is great",
        "variable2":"CDATA is great"
    } 
    return render(request, "authentication/index.html", context)
def about(request):
    return render(request, 'authentication/about.html') 

def contact(request):
    if request.method == "POST":
        ptype=request.POST['ptype']
        psummary=request.POST['psummary']
        pdescription=request.POST['pdescription']
        kanalysis=request.POST['kanalysis']
        kinsights=request.POST['kinsights']
        owner=request.POST['owner']
    
    
        conn = MongoClient()
        db=conn.users
        collection=db.knowledge
        rec1={"ptype":ptype,
          "psummary":psummary,
          "pdescription":pdescription,
          "kanalysis":kanalysis,
          "kinsights":kinsights,
          "owner":owner
        }
        collection.insert_one(rec1)

        # added neo4j database
        neo4j_create_statemenet = "create (k:Knowledge {owner:'ayesha'}), ({psummary:'$psummary'}), ({pdescription:'$pdescription'}),({kanalysis:'$kanalysis'}), ({kinsisghts:'$kinsights'})"
        data_base_connection = GraphDatabase.driver(uri = "bolt://localhost:7687", auth=("neo4j", "admin"))
        session = data_base_connection.session()    
        session.run(neo4j_create_statemenet)

        messages.success(request, 'Your message has been sent!')
    return render(request, 'authentication/contact.html')

def signup(request):
    
    if request.method == "POST":
        username = request.POST.get('username')
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username")
            return redirect('home')
            
        if User.objects.filter(email=email):
            messages.error(request, "Email already registered!")
            return redirect('home')
        
        if len(username)>10:
            messages.error(request, "Username must be under 10 characters")
            
            
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!")
            return redirect('home')
        
     
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()
        
        messages.success(request, " We have sent account activation link to your registered mail id. Kindly click on the link to activate your account .")
        
        
        #welcome email
        
        subject = "Welcome to Knowledge Platform - Django Login!!"
        message = "Hello" + myuser.first_name + "!! \n" + "Welcome to Knowledge Platform!! \n Thank You for visiting our website \n We have also sent you a confirmation email, Please confirm your email address in order to activate yor account. \n\n Thanking You\n Smriti Misra"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        
        #Email Address confirmation email
        
        current_site = get_current_site(request)
        email_subject = "Confirm your email @ Knowledge Platform - Django Login"
        message2 = render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
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
        
        return redirect('signin')
    
    return render(request, "authentication/signup.html")
def index(request):
    print(request.user)
    # if request.user.is_anonymous:
    #     return redirect("/login") 
    return render(request, "authentication/index.html")

def signin(request):  
     
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
    #below we are doing user authentication  
      
        user = authenticate(username=username, password=pass1)   
         
        if user is not None:
             login(request, user)
             fname = user.first_name
             return render(request, "authentication/index.html", {'fname': fname})
             
        else:
            messages.error(request, "Bad Credentials!")
            return redirect('signin')
    
    return render(request, "authentication/signin.html")



def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully")
    return redirect('home')

def activate(request, uidb64, token):
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
        
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')
    
