from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import *
from django.contrib.messages import error
from django.contrib import messages

def index(request):
    return render(request, 'belt_reviewer/index.html')

def create(request):
    errors= User.objects.validate_registration(request.POST)
    if len(errors):
        for field, message in errors.iteritems():
            error(request, message, extra_tags=field)
        return redirect('/')
    else:
        user= User.objects.valid_user(request.POST)
        request.session['user_id']=user.id
        messages.success(request,"registered")
        return redirect('/dashboard')

def login(request):
    errors= User.objects.validate_login(request.POST)
    if len(errors):
        for field, message in errors.iteritems():
            error(request, message, extra_tags=field)
        return redirect('/')
    else:
        user= User.objects.valid_login(request.POST)
        request.session['user_id']=user.id
        messages.success(request,"logged in")
        return redirect('/dashboard')

def dashboard(request):
    try:
        request.session['user_id']
    except KeyError:
        return redirect('/')
    context={
        'user':User.objects.get(id=request.session['user_id']),
        'recentreviews':User.objects.order_by('created_at')[0:3],
    }
    return render(request, 'belt_reviewer/dashboard.html',context)

def addbook(request):
    return render(request, 'belt_reviewer/newbook.html')

def processbook(request):
    entryerrors= Review.objects.validate_review(request.POST,request.session['user_id'])
    if len(entryerrors):
        for k, v in entryerrors.iteritems():
            for k1, v1 in v.items():
                error(request, v1)
        return redirect('/addbook')
    else:
        author= Author.objects.valid_author(request.POST)
        request.session['author_id']=author.id
        book= Book.objects.valid_book(request.POST,author.id)
        request.session['book_id']=book.id
        review= Review.objects.valid_review(request.POST,request.session['book_id'],request.session['user_id'])

        return redirect('/reviews/{}'.format(request.session['book_id']))

def reviews(request, book_id):
    try:
        request.session['book_id']
    except KeyError:
        return redirect('/addbook')
    context={
        'book':Book.objects.get(id=book_id),
        'review':Review.objects.get(book_id=book_id)
    }
    return render(request, 'belt_reviewer/reviews.html',context)

def user(request,user_id):
    user= User.objects.get(id=user_id)
    allreviews=user.user_reviews.all().values("book")
    reviewedbooks={}
    for keys in allreviews:
        for k1,v1 in keys.items():
            books=Book.objects.get(id=v1)
            reviewedbooks[books]=books
    context={
    'user':user,
    'reviewedbooks':reviewedbooks
    }
    return render(request, 'belt_reviewer/user.html',context)
