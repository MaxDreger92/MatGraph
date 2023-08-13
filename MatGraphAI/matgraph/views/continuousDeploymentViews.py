# views.py
import subprocess

from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.crypto import constant_time_compare
from django.views.decorators.http import require_POST
import hmac
import hashlib
from ipware import get_client_ip

@csrf_exempt
@require_POST
def github_webhook(request):
    # Check the X-Hub-Signature header to make sure this is a valid request.
    signature = request.headers.get('X-Hub-Signature-256', '')
    secret = settings.GITHUB_WEBHOOK_SECRET
    mac = hmac.new(secret, msg=request.body, digestmod=hashlib.sha256)
    if not constant_time_compare('sha256=' + mac.hexdigest(), signature):
        return HttpResponseForbidden('Invalid signature')

    # Run the deploy script
    subprocess.Popen(['~/deploy.sh'])

    # If everything went well, return a successful response
    return JsonResponse({'status': 'ok'})






