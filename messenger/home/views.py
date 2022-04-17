from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from accounts.models import Profile
from django.core.mail import EmailMessage
from django.contrib import messages
from .models import *
from .forms import SearchForm
from django.db.models import Q

def main(request):
    category=Category.objects.filter(sub=False)
    gallery=Gallery.objects.all()
    context={'category':category,'gallery':gallery}
    return render(request,'home/main.html',context)

def productss(request,slug=None):
    products=Product.objects.all()
    category=Category.objects.filter(sub=False)
    form=SearchForm()
    exist=False
    if 'search' in request.GET:
        form=SearchForm(request.GET)
        if form.is_valid():
            data=form.cleaned_data['search']
            products=products.filter(Q(name__contains=data)|Q(category__name__contains=data))
            if products:
                exist=True
            else:
                exist=False
    if slug:
        data=get_object_or_404(Category,slug=slug)
        products=products.filter(category=data)
    return render(request,'home/products.html',{'form':form,'products':products , 'category':category,'exist':exist})

def product_detail(request,id):
    product=get_object_or_404(Product,id=id)
    category=Category.objects.filter(sub=False)
    images=Images.objects.filter(product_id=id)
    comment=Comment.objects.filter(product_id=id,is_reply=False)
    comment_form=CommentForm()
    is_like=False
    if product.like.filter(id=request.user.id).exists():
        is_like=True
    is_dislike=False
    if product.dislike.filter(id=request.user.id).exists():
        is_dislike=True
    context={'product':product,'category':category,'is_like':is_like,'is_dislike':is_dislike,'comment':comment,'comment_form':comment_form,'images':images}
    return render(request,'home/detail.html',context)

def product_like(request,id):
    product=get_object_or_404(Product,id=id)
    is_like=False
    if product.like.filter(id=request.user.id).exists():
        product.like.remove(request.user)
        is_like=False
    else:
        product.like.add(request.user)
        is_like=True
    return redirect('home:product_detail',product.id)

def product_dislike(request,id):
    product=get_object_or_404(Product,id=id)
    is_dislike=False
    if product.dislike.filter(id=request.user.id).exists():
        product.dislike.remove(request.user)
        is_dislike=False
    else:
        product.dislike.add(request.user)
        is_dislike=True
    return redirect('home:product_detail',product.id)

def product_comment(request,id):
    if request.method == 'POST':
        comment_form=CommentForm(request.POST)
        if comment_form.is_valid():
            data=comment_form.cleaned_data
            Comment.objects.create(user_id=request.user.id,product_id=id,comment=data['comment'])
            return redirect('home:product_detail',id)
        else:
            return redirect('home:product_detail',id)

def reply_comment(request,id,comment_id):
    if request.method == 'POST':
        comment_form=CommentForm(request.POST)
        if comment_form.is_valid():
            data=comment_form.cleaned_data
            Comment.objects.create(user_id=request.user.id,product_id=id,comment=data['comment'],reply_id=comment_id,is_reply=True)
            return redirect('home:product_detail',id)
        else:
            return redirect('home:product_detail',id)

def contact(request,prof=None):
    if request.method == 'POST':
        subject=request.POST['subject']
        email=request.POST['email']
        msg=request.POST['message']
        body=subject+'\n'+email+'\n'+msg
        form=EmailMessage('contact us',body,'test',('tt.alireza.st.kh@gmail.com',))
        form.send(fail_silently=False)
    return render(request,'home/contact.html')

