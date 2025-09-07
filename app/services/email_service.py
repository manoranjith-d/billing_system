from pathlib import Path

from fastapi.background import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.core.config import settings
from app.core.exceptions import EmailError
from app.db.session import SessionLocal
from app.models.models import Bill as BillModel
from app.schemas.schemas import Bill

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_TLS,
    MAIL_SSL_TLS=settings.MAIL_SSL,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
)


class EmailService:
    def __init__(self):
        self.fastmail = FastMail(conf)

    async def send_bill_email(
        self, background_tasks: BackgroundTasks, customer_email: str, bill: Bill
    ):
        """Send bill details to customer email asynchronously"""
        try:
            db = SessionLocal()
            # Create message schema
            message = MessageSchema(
                subject="Your Bill Details",
                recipients=[customer_email],
                template_body={
                    "bill": bill,
                    "total_amount": bill.total_amount,
                    "tax_amount": bill.tax_amount,
                    "paid_amount": bill.paid_amount,
                    "balance_amount": bill.balance_amount,
                    "items": bill.items,
                },
                subtype="html",
            )

            # Add email sending task to background tasks
            background_tasks.add_task(
                self.fastmail.send_message, message, template_name="bill_email.html"
            )
            try:
                bill = db.query(BillModel).filter(BillModel.id == bill.id).first()
                if bill:
                    bill.mail_sent = True
                db.commit()
            except Exception as e:
                print("error", str(e))

        except Exception as e:
            raise EmailError(f"Failed to send email: {str(e)}")
        finally:
            db.close()

    async def send_test_email(self, email: str):
        """Send a test email to verify email configuration"""
        try:
            message = MessageSchema(
                subject="Test Email",
                recipients=[email],
                body="This is a test email from the billing system.",
                subtype="plain",
            )

            await self.fastmail.send_message(message)
            return {"message": "Test email sent successfully"}

        except Exception as e:
            raise EmailError(f"Failed to send test email: {str(e)}")
