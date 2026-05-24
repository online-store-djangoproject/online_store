from django.core.mail import send_mail
from django.conf import settings

def send_discount_email(user, discount_code):
    """ ارسال ایمیل کد تخفیف به کاربر """
    subject = "🎉 کد تخفیف ماهانه شما"
    message = (
        f"سلام {user.first_name or user.email}!\n\n"
        f"کد تخفیف ویژه شما: {discount_code}\n"
        "این کد تا پایان این ماه معتبر است و می‌توانید هنگام خرید از آن استفاده کنید.\n\n"
        "با تشکر، تیم فروشگاه"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
