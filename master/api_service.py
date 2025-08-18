import razorpay
from django.conf import settings

class PaymentService:
    def __init__(self):
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def create_order(self, amount, currency="INR"):
        """Creates a payment order"""
        data = {
            "amount": amount * 100,  # Razorpay accepts amount in paise
            "currency": currency,
            "payment_capture": 1  # Auto-capture after successful payment
        }
        return self.client.order.create(data)

    def verify_payment(self, razorpay_payment_id, razorpay_order_id, razorpay_signature):
        """Verifies payment signature to ensure security"""
        return self.client.utility.verify_payment_signature({
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_order_id": razorpay_order_id,
            "razorpay_signature": razorpay_signature
        })
