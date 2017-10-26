from __future__ import unicode_literals
import re
import bcrypt
from django.db import models

EMAIL_REGEX=re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
NAME_REGEX=re.compile(r'^[a-zA-Z]+$')

class UserManager(models.Manager):
    def validate_login(self,post_data):
        errors={}
        if len(self.filter(email=post_data['email']))>0:
            user=self.filter(email=post_data['email'])[0]
            if not bcrypt.checkpw(post_data['password'].encode(), user.password.encode()):
                errors['login']="Email/password is incorrect"
        else:
            errors['login']="Email/password is incorrect"
        return errors

    def valid_login(self,post_data):
        if len(self.filter(email=post_data['email']))>0:
            user=self.filter(email=post_data['email'])[0]
        return user

    def validate_registration(self,post_data):
        errors={}
        for field,value in post_data.iteritems():

            if len(value)<1:
                errors[field]="{} field is required".format(field.replace('_',' '))

            if field == "first_name" or field =="last_name":
                if not field in errors and len(value) < 3:
                    errors[field]="{} field must be at least 3 characters".format(field.replace('_',' '))
                elif not field in errors and not re.match(NAME_REGEX,post_data[field]):
                    errors[field]="Invalid characters in {} field".format(field.replace('_',' '))

            if field == "password":
                if not field in errors and len(value) <8:
                    errors[field]="{} field must be at least 8 characters".format(field.replace('_',' '))
                elif post_data['password'] != post_data['confirmpw']:
                    errors[field]="{} do not match".format(field.replace('_',''))

            if field == "email":
                if not field in errors and not re.match(EMAIL_REGEX, post_data[field]):
                    errors[field]="Invalid {}".format(field)
                elif len(self.filter(email=post_data['email']))> 0:
                    errors[field]= "{} is already in use".format(field)

        return errors

    def create_user(self,post_data):
        hashed= bcrypt.hashpw(post_data['password'].encode(), bcrypt.gensalt(5))
        new_user= self.create(
            first_name= post_data['first_name'],
            last_name= post_data['last_name'],
            email= post_data['email'],
            password= hashed
        )
        return new_user

class User(models.Model):
    first_name= models.CharField(max_length=255)
    last_name= models.CharField(max_length=255)
    email= models.CharField(max_length=255)
    password= models.CharField(max_length=255)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    objects = UserManager()
    def __repr__(self):
        return "id:{} first_name:{} last_name:{} email:{} created_at:{} updated_at:{}".format(self.id,self.first_name,self.last_name,self.email,self.created_at,self.updated_at)

class AuthorManager(models.Manager):
    def create_author(self,post_data):
        new_author= self.create(
            name= post_data['name']
        )
        return new_author

class Author(models.Model):
    name= models.CharField(max_length=255)
    created_at= models.DateTimeField(auto_now_add= True)
    updated_at= models.DateTimeField(auto_now= True)
    objects= AuthorManager()
    def __repr__(self):
        return "id {} name{} books{}".format(self.id, self.name,self.books)

class BookManager(models.Manager):

    def create_book(self,post_data,author_id):
        new_book= self.create(
            title= post_data['title'],
            author_id=author_id
        )
        return new_book

class Book(models.Model):
    title= models.CharField(max_length=255,null=True)
    author=models.ForeignKey(Author,related_name="books",null=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    objects=BookManager()
    def __repr__(self):
        return "id:{} title:{} author: {}".format(self.id,self.title,self.author)


class ReviewManager(models.Manager):
    def validate_newreview(self,post_data,user_id):

        errors={}

        for field,value in post_data.iteritems():

            if len(value)<1:
                errors[field]="{} field is required".format(field.replace('_',' '))

            elif field == "name":
                if not field in errors and len(Author.objects.filter(name=post_data['name']))> 0:
                    errors[field]= "{} has already been submitted".format(field)

            elif field == "title":
                if not field in errors and len(Book.objects.filter(title=post_data['title']))> 0:
                    errors[field]= "{} has already been submitted".format(field)

        return errors

    def validate_review(self,post_data,user_id,book_id):

        errors={}

        for field,value in post_data.iteritems():

            if len(self.filter(reviewer_id=user_id,book_id=book_id))> 0:
                errors[field]= "User has already submitted a review"

            if len(value)<1:
                errors[field]="{} field is required".format(field.replace('_',' '))



        return errors

    def add_review(self,post_data,book_id,user_id):
        new_review= self.create(
            desc= post_data['desc'],
            rating= post_data['rating'],
            book_id=book_id,
            reviewer_id=user_id,
        )
        return new_review

class Review(models.Model):
    desc= models.TextField()
    rating= models.IntegerField()
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    reviewer=models.ForeignKey(User, related_name="user_reviews", null=True)
    book=models.ForeignKey(Book, related_name="book_reviews", null=True)
    objects = ReviewManager()
    def __repr__(self):
        return "id {} desc {} rating {} created_at{} book{} reviewer{}".format(self.id,self.desc,self.rating,self.created_at,self.book_id,self.reviewer_id)
