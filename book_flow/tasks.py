import logging
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mass_mail
from django.conf import settings
from book_flow.models import BorrowHistory

logger = logging.getLogger(__name__)


@shared_task
def notify_users():
    try:
        now = timezone.now()
        overdue_borrowings = BorrowHistory.objects.filter(due_date__lt=now, returned=False)

        emails = []
        for borrow in overdue_borrowings:
            subject = f'Overdue Book Reminder: {borrow.book.title}'
            message = f'Dear {borrow.borrower.full_name},\n\n'
            message += f'This is a friendly reminder that the book "{borrow.book.title}" is overdue for return.\n'
            message += 'Please return the book as soon as possible to avoid any penalties.\n\n'
            message += 'Thank you for your cooperation.'
            from_email = settings.EMAIL_HOST_USER
            recipient = borrow.borrower.email

            emails.append((subject, message, from_email, [recipient]))
        send_mass_mail(tuple(emails))
        logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
