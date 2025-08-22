
class NgrokSkipBrowserWarningMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'ngrok-skip-browser-warning' not in request.headers:
            request.META['HTTP_NGROK_SKIP_BROWSER_WARNING'] = 'true'
        return self.get_response(request)
