from django.shortcuts import render , redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from django.contrib.auth import authenticate , login , logout
from .forms import *
from django.contrib.auth.decorators import login_required
from posts.models import *

# Create your views here.

def like(request):
    postId = request.POST['postId']
    post = Post.objects.get(id = postId)
    if 'like' in request.POST:
        if request.user.profile in post.like.all():
            post.like.remove(request.user.profile)
            post.save()
        else:
            post.like.add(request.user.profile)
            post.dislike.remove(request.user.profile)
            post.save()
    if 'dislike' in request.POST :
        if request.user.profile in post.dislike.all():
            post.dislike.remove()
            post.save()
        else:
            post.dislike.add(request.user.profile)
            post.like.remove(request.user.profile)
            post.save()
            
def userRegister(request):
    username = ''
    email = ''
    name = ''
    surname = ''
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        name = request.POST['name']
        surname = request.POST['surname']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1==password2:
            if User.objects.filter(username = username).exists():
                messages.error(request , 'Bu kullanici adi zaten alinmis')
            elif User.objects.filter(email=email).exists():
                messages.error(request , 'Bu email zaten alinmis')
            elif len(password1)<6:
                messages.error(request , 'Sifreniz en az 6 karakter olmalidir')
            elif username.lower() in password1:
                messages.error(request , 'Sifrenizde kullanici adinizi kullanamazsiniz')        
            else:
                user = User.objects.create_user(username=username , email=email , password=password1)     
                user.save()
                Profile.objects.create(
                    user = user , 
                    name = name , 
                    surname = surname
                )
                messages.success(request , 'Basariyls Kayit oldunuz.')
                return redirect('index')
        else:
            messages.error(request , 'Sifreleriniz Olusmuyor')    
    context = {
        'username' : username,
        'email' : email,
        'name': name,
        'surname': surname,
        }        
    return render(request , 'user/register.html', context)

def userLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request , username=username , password=password)

        if user is not None:
            login(request , user)
            messages.success(request , 'Giris Yapildi')
            return redirect('index')
        else:
            messages.error(request , 'Kullanici adi veya sifre hatali !' )
            return redirect('login') 
    return render(request , 'user/login.html')    

def userLogout(request):
    logout(request)
    messages.success(request , 'Cikis yapildi')
    return redirect('index')

def profile(request , slug):
    profil = Profile.objects.get(slug = slug)
    paylasim = Post.objects.filter(owner = profil)
    begen = Post.objects.filter(like__in = [profil ])
    if request.method == 'POST':
        if request.user.is_authenticated:
            if 'takip' in request.POST:
                hesabim = Profile.objects.get(user = request.user)
                if Profile.objects.filter(slug = slug , followers__in = [hesabim]).exists():
                    profil.followers.remove(hesabim)
                    hesabim.follow.remove(profil)
                    messages.success(request , f'{profil.user.username} kullanicisini takip etmeyi biraktiniz. ')
                    return redirect('profile' , slug =  profil.slug)
                else:
                    profil.followers.add(hesabim)
                    hesabim.follow.add(profil)    
                    messages.success(request , f'{profil.user.username} kullanicisini takip etmeye basladiniz. ')
                    return redirect('profile' , slug =  profil.slug)
            elif 'sil' in request.POST:
                postId = request.POST['postId']
                post = Post.objects.get(id=postId)
                post.delete()
                messages.success(request , 'Paylasim silsindi')
                return redirect('profile' , slug=slug)
            else:
                like(request)   
                return redirect('profile' , slug =  profil.slug) 
        else:
            messages.error(request , 'Lutfen giris yapiniz')
            return redirect('login')
    context = {
        'profil':profil,
        'paylasim':paylasim,
        'begen':begen
    }
    return render(request , 'user/profil.html' , context)

@login_required(login_url='login')
def update(request):
    myUser = request.user
    myProfile = request.user.profile
    form = UserForm(instance = myUser)
    profilForm = ProfilForm(instance=myProfile)
    if request.method == 'POST':
        form = UserForm(request.POST , instance=myUser)
        profilForm = ProfilForm(request.POST , request.FILES , instance=myProfile)
        if form.is_valid() and profilForm.is_valid():
            form.save()
            profilForm.save()
            messages.success(request , 'Profiliniz guncellendi')
            return redirect('profile' , slug = myProfile.slug)

    context = {
        'form':form,
        'profilForm':profilForm
    }
    return render(request , 'user/update.html' , context)

@login_required(login_url='login')
def reset(request):
    myUser = request.user
    if request.method == 'POST':
        eski = request.POST['eski']
        yeni = request.POST['yeni']
        confirm =request.POST['confirm']

        user = authenticate(request , username = request.user , password = eski)

        if user is not None:
            if yeni == confirm:
                myUser.set_password('yeni')
                myUser.save()
                messages.success(request , 'Sifreniz guncellendi')
                return redirect('login')
        else:
            messages.error(request , 'Mevcut sifre hatali')
    return render(request , 'user/password.html')        
