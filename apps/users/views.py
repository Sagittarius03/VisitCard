from django.shortcuts import render

from utils.text_format import printf

# Create your views here.
def profile(request):
    try: 
        user = request.user
        
        return render(request, 'users/profile.jinja', {
            'text': user
        }, using='jinja2')
    except Exception as err:
        printf(f"<error>Ошибка профиля: {err}</error>")
        