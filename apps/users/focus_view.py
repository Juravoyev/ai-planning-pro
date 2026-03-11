from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def focus_view(request):
    return render(request, 'focus/focus.html')
