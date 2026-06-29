from django.shortcuts import render

def home(request):
    return render(request, "base.jinja", using='jinja2', 
        context={
            
    })