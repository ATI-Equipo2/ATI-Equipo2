from django.shortcuts import render

from django.shortcuts import render
from django.utils import timezone
from .models import Post

def post_list(request):
    posts =Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    # Pasamos los posts al archivo HTML mediante el contexto
    return render(request, 'MyDjangoApp/post_list.html', {'posts':
    posts})
