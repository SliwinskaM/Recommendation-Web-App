from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


# Create your views here.
@login_required
def home_view(request, *args, **kwargs):
    return render(request, "home.html", {})




