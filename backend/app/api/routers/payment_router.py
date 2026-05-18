import os
import stripe
import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from backend.app.dependencies import get_current_user_id, get_credit_service
from backend.app.services.credit_service import CreditService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/payment",
    tags=["payment"]
)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_replace_me")

# Predefined credit packages (Secure pricing defined on the backend)
PACKAGES = {
    "pack_10": {
        "name": "Pakiet 10 Kredytów - Auto Tests AI",
        "amount": 1000,        # 10.00 PLN in grosze
        "credits": 10,
        "currency": "pln"
    },
    "pack_50": {
        "name": "Pakiet 50 Kredytów - Auto Tests AI",
        "amount": 4000,        # 40.00 PLN in grosze (10 credits free!)
        "credits": 50,
        "currency": "pln"
    },
    "pack_100": {
        "name": "Pakiet 100 Kredytów - Auto Tests AI",
        "amount": 7000,        # 70.00 PLN in grosze (30 credits free!)
        "credits": 100,
        "currency": "pln"
    }
}

class CheckoutSessionRequest(BaseModel):
    package_id: str  # must be one of "pack_10", "pack_50", "pack_100"
    success_url: str = "http://localhost:5173/success?session_id={CHECKOUT_SESSION_ID}"
    cancel_url: str = "http://localhost:5173/cancel"

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Creates a secure Stripe Checkout Session linked to the authenticated user ID.
    """
    if request.package_id not in PACKAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid package_id. Choose from: {list(PACKAGES.keys())}"
        )
        
    package = PACKAGES[request.package_id]
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": package["currency"],
                        "product_data": {
                            "name": package["name"],
                            "description": f"Kupujesz {package['credits']} kredytów do generowania i naprawiania testów językowych."
                        },
                        "unit_amount": package["amount"],
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            client_reference_id=user_id,  # Securely tie this payment to the Supabase user UUID
            metadata={
                "credits": str(package["credits"]),
                "package_id": request.package_id
            },
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )
        return {"id": session.id, "url": session.url}
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    credit_service: CreditService = Depends(get_credit_service)
):
    """
    Stripe Webhook listener. Automatically handles completed checkout sessions
    and grants credits to the corresponding user in the database.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    event = None

    try:
        if endpoint_secret and sig_header:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        else:
            # Fallback for development if STRIPE_WEBHOOK_SECRET is not configured
            import json
            logger.warning("STRIPE_WEBHOOK_SECRET is not set. Extracting event without verification (Dev Mode only).")
            event = json.loads(payload.decode("utf-8"))
    except ValueError as e:
        logger.error(f"Invalid Webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid Webhook signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.get("type") if isinstance(event, dict) else event.type

    if event_type == "checkout.session.completed":
        session = event["data"]["object"] if isinstance(event, dict) else event.data.object
        
        user_id = session.get("client_reference_id")
        metadata = session.get("metadata", {})
        credits_to_add = int(metadata.get("credits", 0))
        package_id = metadata.get("package_id")

        if user_id and credits_to_add > 0:
            logger.info(f"Stripe Webhook: Crediting {credits_to_add} credits to user {user_id} (package: {package_id})")
            credit_service.add_credits(user_id, credits_to_add)
        else:
            logger.warning(f"Stripe Webhook received checkout.session.completed but user_id or credits were missing/invalid. User: {user_id}, Credits: {credits_to_add}")

    return {"status": "success"}

