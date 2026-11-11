from django.shortcuts import render

def dashboard_view(request):
    """Отрисовка основного интерфейса дашборда."""
    return render(request, 'dashboard/index.html')