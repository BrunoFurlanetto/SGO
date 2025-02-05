from django.http import JsonResponse
from functools import wraps


def require_ajax(view_func):
    """
    Decorator para verificar se a requisição é AJAX.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Esta requisição deve ser AJAX.'}, status=400)

        return view_func(request, *args, **kwargs)
    return _wrapped_view
