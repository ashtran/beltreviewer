from __future__ import unicode_literals
import re
import bcrypt
from django.db import models

EMAIL_REGEX=re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
NAME_REGEX=re.compile(r'^[a-zA-Z]+$')

class UserManager(models.Manager):
# <--- Validate User Login---> #
    def validate_login(self,post_data):
        errors={}
        login=self.filter(email=post_data['email'])
        # <- Get Login Email -> #
        if len(login)>0:
            user=login[0]
            hashed = bcrypt.hashpw(post_data['password'].encode(), bcrypt.gensalt())
            # <- Password -> #
            if not bcrypt.checkpw(user.password.encode(), hashed):
                errors['login']="Email/password is incorrect"
        # <- Blank Field -> #
        else:
            errors['login']="Email/password is incorrect"

        return errors

# <--- Validate User Registration---> #
    def validate_registration(self,post_data):
        errors={}
        for field,value in post_data.items():
            # <- Blank Entry -> #
            if len(value)<1:
                errors[field]="{} field is required".format(field.replace('_',' '))
            # <- Name Length & Alpha Format -> #
            if field == "first_name" or field =="last_name":
                if not field in errors and len(value) < 3:
                    errors[field]="{} field must be at least 3 characters".format(field.replace('_',' '))
                elif not field in errors and not re.match(NAME_REGEX,post_data[field]):
                    errors[field]="Invalid characters in {} field".format(field.replace('_',' '))
            # <- Password Length & Match-> #
            if field == "password":
                if not field in errors and len(value) <8:
                    errors[field]="{} field must be at least 8 characters".format(field.replace('_',' '))
                elif post_data['password'] != post_data['confirmpw']:
                    errors[field]="{} do not match".format(field.replace('_',''))
            # <- Email Format & Exists -> #
            if field == "email":
                if not field in errors and not re.match(EMAIL_REGEX, post_data[field]):
                    errors[field]="Invalid {}".format(field)
                elif len(self.filter(email=post_data['email']))> 0:
                    errors[field]= "{} is already in use".format(field)

        return errors

# <--- Create User Account ---> #
    def create_user(self,post_data):
        new_user= self.create(
            first_name= post_data['first_name'],
            last_name= post_data['last_name'],
            email= post_data['email'],
            password= post_data['password']
        )
        return new_user

class User(models.Model):
# <--- User Attributes ---> #
    first_name= models.CharField(max_length=255)
    last_name= models.CharField(max_length=255)
    email= models.CharField(max_length=255)
    password= models.CharField(max_length=255)

    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    objects = UserManager()
    # <- Print class attributes -> #
    def __repr__(self):
        return "id:{} first_name:{} last_name:{} email:{} created_at:{} updated_at:{}".format(self.id,self.first_name,self.last_name,self.email,self.created_at,self.updated_at)


class AuthorManager(models.Manager):
# <--- Create Author ---> #
    def create_author(self,post_data):
        new_author= self.create(
            name= post_data['name']
        )
        return new_author

class Author(models.Model):
# <--- Author Attributes ---> #
    name= models.CharField(max_length=255)

    created_at= models.DateTimeField(auto_now_add= True)
    updated_at= models.DateTimeField(auto_now= True)

    objects= AuthorManager()
    # <- Print class attributes -> #
    def __repr__(self):
        return "id {} name{} books{}".format(self.id, self.name,self.books)


class BookManager(models.Manager):
# <--- Create Book ---> #
    def create_book(self,post_data,author_id):
        new_book= self.create(
            title= post_data['title'],
            author_id=author_id
        )
        return new_book

class Book(models.Model):
# <--- Book Attributes ---> #
    title= models.CharField(max_length=255,null=True)
    author=models.ForeignKey(Author,related_name="books",null=True, on_delete=models.PROTECT)

    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    objects=BookManager()
# <- Print class attributes -> #
    def __repr__(self):
        return "id:{} title:{} author: {}".format(self.id,self.title,self.author)


class ReviewManager(models.Manager):
# <--- Validate New Review Entry ---> #
    def validate_newreview(self,post_data,user_id):
        errors={}
        for field,value in post_data.items():
            # <- Blank Field -> #
            if len(value)<1:
                errors[field]="{} field is required".format(field.replace('_',' '))
            # <- Author Exists -> #
            elif field == "name":
                if not field in errors and len(Author.objects.filter(name=post_data['name']))> 0:
                    errors[field]= "Author has already been submitted"
            # <- Book Exists -> #
            elif field == "title":
                if not field in errors and len(Book.objects.filter(title=post_data['title']))> 0:
                    errors[field]= "Book has already been submitted"

        return errors
# <--- Validate Add Review ---> #
    def validate_review(self,post_data,user_id,book_id):
        errors={}
        for field,value in post_data.items():
            # <- User Review Exists -> #
            if len(self.filter(reviewer_id=user_id,book_id=book_id))> 0:
                errors[field]= "User has already submitted a review"
            # <- Blank Review -> #
            if len(value)<1:
                errors[field]="{} field is required".format(field.replace('_',' '))

        return errors
# <--- Create Review ---> #
    def add_review(self,post_data,book_id,user_id):
        new_review= self.create(
            desc= post_data['desc'],
            rating= post_data['rating'],
            book_id=book_id,
            reviewer_id=user_id,
        )
        return new_review

class Review(models.Model):
# <--- Review attributes ---> #
    desc= models.TextField()
    rating= models.IntegerField()
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    reviewer=models.ForeignKey(User, related_name="user_reviews", null=True, on_delete=models.PROTECT)
    book=models.ForeignKey(Book, related_name="book_reviews", null=True,on_delete=models.PROTECT)
    objects = ReviewManager()
    # <- Print class attributes -> #
    def __repr__(self):
        return "id {} desc {} rating {} created_at{} book{} reviewer{}".format(self.id,self.desc,self.rating,self.created_at,self.book_id,self.reviewer_id)
