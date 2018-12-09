from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from .models import *
from django.contrib.messages import error
from django.contrib import messages

def index(request):
    return render(request, 'belt_reviewer/index.html')

def createuser(request):
    errors= User.objects.validate_registration(request.POST)
    if len(errors):
        for field, message in errors.items():
            error(request, message, extra_tags=field)
        return redirect('/')
    else:
        user= User.objects.create_user(request.POST)
        request.session['user_id']=user.id
        return redirect('/dashboard')

def login(request):
    errors= User.objects.validate_login(request.POST)
    if len(errors):
        for field, message in errors.items():
            error(request, message, extra_tags=field)
        return redirect('/')
    else:
        user= User.objects.filter(email=request.POST['email'])[0]
        request.session['user_id']=user.id
        return redirect('/dashboard')

def dashboard(request):
    #<--- Check if logged in/in session --->
    try:
        request.session['user_id']
    except KeyError:
        return redirect('/')

    recentreviews=Review.objects.order_by('-created_at')[0:3].all()
    booksreviewed=Review.objects.order_by('-created_at').all()
    context={
        'user':User.objects.get(id=request.session['user_id']),
        'recentreviews':recentreviews,
        'booksreviewed':booksreviewed,
    }
    return render(request, 'belt_reviewer/dashboard.html',context)

def addbook(request):
    #<--- Check if logged in/in session --->
    try:
        request.session['user_id']
    except KeyError:
        return redirect('/')

    context={
        'authors':Author.objects.all()
    }
    return render(request, 'belt_reviewer/newbook.html',context)

def processbook(request):
    errors= Review.objects.validate_newreview(request.POST,request.session['user_id'])
    if len(errors):
        for field, message in errors.items():
            error(request, message, extra_tags=field)
        return redirect('/addbook')

    else:
        new_author= Author.objects.create_author(request.POST)
        new_book= Book.objects.create_book(request.POST,new_author.id)
        newentry= Review.objects.add_review(request.POST,new_book.id,request.session['user_id'])

        return redirect('/reviews/{}'.format(new_book.id))

def reviews(request, book_id):
    review=Review.objects.filter(book_id=book_id)
    user_reviews=Review.objects.filter(reviewer_id=request.session['user_id'],book_id=book_id)

    try:
        request.session['user_id']
        user_reviews=user_reviews
    except KeyError:
        return

    context={
        'book': Book.objects.get(id=book_id),
        'review': review,
        'authors': Author.objects.all(),
        'user_reviews': user_reviews,
        'user':request.session['user_id']
    }
    return render(request, 'belt_reviewer/reviews.html',context)

def delete(request,book_id):
    delete_review=Review.objects.filter(book_id=book_id,reviewer_id=request.session['user_id']).delete()
    #print delete_review
    return redirect('/reviews/{}'.format(book_id))

def addreview(request,book_id):
    errors=Review.objects.validate_review(request.POST,request.session['user_id'],book_id)
    if len(errors):
        for field, message in errors.items():
            error(request,message, extra_tags=field)
            return redirect('/reviews/{}'.format(book_id))
    else:
        new_review= Review.objects.add_review(request.POST,book_id, request.session['user_id'])
        return redirect('/reviews/{}'.format(book_id))

def user(request,user_id):
    user= User.objects.get(id=user_id)
    context={
        'user':user,
        'reviewedbooks':Review.objects.filter(reviewer_id=user.id)
    }
    return render(request, 'belt_reviewer/user.html',context)

def logout(request):
    del request.session['user_id']
    return redirect('/')
