import os
from supabase import Client, create_client
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class CreditService:
    def __init__(self):
        self.supabase: Client = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_KEY")
        )

    def deduct_credit(self, email: str):
        try:
            logger.info(f"Deducting credit for user: {email}")
            response = self.supabase.table("Account").select("credits").eq("email", email).execute()
            if not response.data or len(response.data) == 0:
                logger.error(f"User not found for credit deduction: {email}")
                raise HTTPException(status_code=404, detail="User not found")
            
            current_credits = response.data[0].get("credits", 0)
            if current_credits <= 0:
                logger.warning(f"User {email} has not enough credits: {current_credits}")
                raise HTTPException(status_code=403, detail="Not enough credits")
            
            # Deduct 1 credit
            update_response = self.supabase.table("Account").update({"credits": current_credits - 1}).eq("email", email).execute()
            return update_response.data
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deducting credit for {email}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
