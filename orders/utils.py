from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def notificar_estado_orden(order):
    subject = f"Tu orden #{order.order_number} ha cambiado de estado"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [order.buyer.email]

    context = {
        'order': order,
        'user': order.buyer,
        'domain': 'http://127.0.0.1:8000'  # o http://127.0.0.1:8000 para desarrollo local
    }

    html_content = render_to_string('orders/emails/order_status_update.html', context)
    text_content = f"""
Tu orden #{order.order_number} cambió de estado a: {order.get_status_display()}.

Producto: {order.product.name}
Total: ${order.total_price}
Fecha: {order.created_at.strftime('%d/%m/%Y %H:%M')}
"""

    msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    msg.send()