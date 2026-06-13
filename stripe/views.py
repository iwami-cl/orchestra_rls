from django.shortcuts import render

# Create your views here.
import json
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .models import Product
from .models import Price


# STRIPEのシークレットキー
stripe.api_key = "dummy_stripe_secret_key"  # ここは実際のシークレットキーに置き換えてください

# WEBHOOKのシークレットキー
endpoint_secret = "dummy_stripe_webhook_secret"  # ここは実際のWebhookシークレットキーに置き換えてください

# 商品購入時のWebHookを受け取るためのビュー
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # ここで購入完了後の処理を行う（例: データベースの更新、メールの送信など）
        # 例: 購入者のメールアドレスを取得して確認メールを送信する
        # 後で作るので今はprintするだけ
        print(f"購入が完了しました。購入者のメールアドレス: {session['customer_email']}")

    return HttpResponse(status=200)