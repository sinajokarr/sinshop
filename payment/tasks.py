from celery import shared_task
import time

@shared_task
def send_payment_notification(order_id, email):
    print(f"Starting to generate receipt for Order {order_id}...")
    time.sleep(5) 
    print(f"Receipt sent to {email} successfully!")
    return True