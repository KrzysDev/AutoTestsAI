import os
from supabase import Client, create_client
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class CreditService:
    def __init__(self):
        self.supabase: Client = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_SERVICE_KEY")
        )

    def deduct_credit(self, user_id: str):
        try:
            logger.info(f"Deducting credit for user: {user_id}")
            response = self.supabase.table("Credits").select("credits").eq("id", user_id).execute()
            if not response.data or len(response.data) == 0:
                logger.error(f"User not found for credit deduction: {user_id}")
                raise HTTPException(status_code=404, detail="User not found")
            
            current_credits = response.data[0].get("credits", 0)
            if current_credits <= 0:
                logger.warning(f"User {user_id} has not enough credits: {current_credits}")
                raise HTTPException(status_code=403, detail="Not enough credits")
            
            # Deduct 1 credit
            update_response = self.supabase.table("Credits").update({"credits": current_credits - 1}).eq("id", user_id).execute()
            return update_response.data
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deducting credit for {user_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
