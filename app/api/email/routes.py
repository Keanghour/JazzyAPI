from fastapi import APIRouter, HTTPException, Depends
from app.core.email import send_email
from app.schemas.auth import EmailRequest

email = APIRouter()

@email.post("/send-email", status_code=200)
async def send_email_route(email_request: EmailRequest):
    try:
        await send_email(
            to_email=email_request.to_email,
            subject=email_request.subject,
            body=email_request.message
        )
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
