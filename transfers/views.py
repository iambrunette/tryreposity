import random
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from jsonrpcserver import method, dispatch
from .models import Transfer, Card
from django.utils.timezone import now
from datetime import datetime
from .services.transfer_service import send_telegram_notification
from django.contrib.auth import get_user_model

User = get_user_model()

def transfer_view(request):
    # ... логика транзакции ...
    try:
        transfer = Transfer.objects.create(
        amount=request.POST.get('amount'),
        status='PENDING'
        )
        
        # 2. Обрабатываем транзакцию
        transfer.status = 'SUCCESS'
        transfer.save()
        
        # 3. Отправляем уведомление
        send_telegram_notification(
            chat_id=request.user.telegram_id,
            message=f"Перевод на {transfer.amount}₸ выполнен!"  # Исправлено sending_samount → amount
        )
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({"message": "Transfer processed successfully"}
        )

# ======= Вспомогательные функции =======
def generate_otp(length=6):
    return str(random.randint(10**(length-1), 10**length - 1))

def send_telegram_message(phone, message, chat_id=123456):
    # Здесь будет интеграция с Telegram Bot API
    print(f"[Telegram] Отправка на {phone}: {message}")

def luhn_check(card_number: str) -> bool:
    """Проверка номера карты по алгоритму Луна"""
    digits = [int(d) for d in card_number]
    checksum = 0
    parity = len(digits) % 2
    for i, digit in enumerate(digits):
        if i % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0

def validate_card(card_number, expiry):
    """Проверка карты по ТЗ"""
    if not luhn_check(card_number):
        return False, "Invalid card number"

    try:
        card = Card.objects.get(card_number=card_number, expiry=expiry)
    except Card.DoesNotExist:
        return False, "Card not found"

    if not card.active:
        return False, "Card is inactive"

    if not card.phone:
        return False, "Phone not linked to card"

    return True, card


def get_transfer_by_ext_id(ext_id):
    try:
        return Transfer.objects.get(ext_id=ext_id)
    except Transfer.DoesNotExist:
        return None


# ======= JSON-RPC методы =======

@method
def transfer_create(ext_id, sender_card_number, sender_card_expiry, receiver_card_number, sending_amount, currency):
    # Проверка уникальности ext_id
    if Transfer.objects.filter(ext_id=ext_id).exists():
        return {"error": "ext_id already exists"}

    # Валидация отправителя
    valid, sender_card = validate_card(sender_card_number, sender_card_expiry)
    if not valid:
        return {"error": sender_card}

    # Проверка баланса
    if sender_card.balance < sending_amount:
        return {"error": "Insufficient funds"}

    # Валидация получателя
    valid, receiver_card = validate_card(receiver_card_number, None)
    if not valid:
        return {"error": receiver_card}

    # Проверка валюты
    if currency not in [643, 840]:
        return {"error": "Invalid currency"}

    # Генерация OTP
    otp_code = generate_otp()
    send_telegram_message(sender_card.phone, f"Your OTP: {otp_code}")

    # Создание перевода
    transfer = Transfer.objects.create(
        ext_id=ext_id,
        sender_card_number=sender_card_number,
        sender_card_expiry=sender_card_expiry,
        receiver_card_number=receiver_card_number,
        sending_amount=sending_amount,
        currency=currency,
        otp=otp_code,
        state="created",
        try_count=0
    )

    return {"ext_id": transfer.ext_id, "state": transfer.state, "otp_sent": True}


@method
def transfer_confirm(ext_id, otp):
    transfer = get_transfer_by_ext_id(ext_id)
    if not transfer:
        return {"error": "Transfer not found"}

    if transfer.state != "created":
        return {"error": "Transfer already processed"}

    if transfer.try_count >= 3:
        return {"error": "Too many incorrect attempts"}

    if transfer.otp != otp:
        transfer.try_count += 1
        transfer.save()
        return {"error": f"Incorrect OTP. Attempts left: {3 - transfer.try_count}"}

    # Подтверждение
    transfer.state = "confirmed"
    transfer.confirmed_at = now()
    transfer.save()

    return {"ext_id": transfer.ext_id, "state": transfer.state}


@method
def transfer_cancel(ext_id):
    transfer = get_transfer_by_ext_id(ext_id)
    if not transfer:
        return {"error": "Transfer not found"}

    if transfer.state != "created":
        return {"error": "Transfer cannot be canceled"}

    transfer.state = "cancelled"
    transfer.cancelled_at = now()
    transfer.save()

    return {"ext_id": transfer.ext_id, "state": transfer.state}


@method
def transfer_state(ext_id):
    transfer = get_transfer_by_ext_id(ext_id)
    if not transfer:
        return {"error": "Transfer not found"}

    return {
        "ext_id": transfer.ext_id,
        "state": transfer.state,
        "sender_card_number": transfer.sender_card_number,
        "receiver_card_number": transfer.receiver_card_number,
        "sending_amount": transfer.sending_amount,
        "currency": transfer.currency
    }


@method
def transfer_history(card_number=None, start_date=None, end_date=None, status=None):
    qs = Transfer.objects.all()

    if card_number:
        qs = qs.filter(sender_card_number=card_number)

    if start_date:
        qs = qs.filter(created_at__gte=datetime.fromisoformat(start_date))

    if end_date:
        qs = qs.filter(created_at__lte=datetime.fromisoformat(end_date))

    if status:
        qs = qs.filter(state=status)

    return list(qs.values("ext_id", "sending_amount", "state", "created_at"))


@csrf_exempt
def jsonrpc_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return JsonResponse({"info": "Use POST with JSON-RPC payload"}, status=200)

    try:
        if not request.body:
            return JsonResponse({
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Empty request body"},
                "id": None
            }, status=400)

        body_str = request.body.decode()
        response = dispatch(body_str)
        return JsonResponse(response, safe=False)

    except UnicodeDecodeError:
        return JsonResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Invalid encoding"},
            "id": None
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": "Internal error", "data": str(e)},
            "id": None
        }, status=500)
