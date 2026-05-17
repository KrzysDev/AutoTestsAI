from fastapi import APIRouter, HTTPException, Depends
import os

from supabase import Client, create_client
from backend.app.dependencies import get_current_user_id

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

router = APIRouter()

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_SERVICE_KEY")
)


@router.post("/v1/auth/check_account_table")
def check_account_table(user_id: str = Depends(get_current_user_id)):
    """
    Ensures the authenticated user has an entry in the Credits table.
    If not, creates one with 0 credits. Uses JWT token for user identification.
    """
    try:
        response = (
            supabase.table("Credits")
            .select("*")
            .eq("id", user_id)
            .execute()
        )

        if len(response.data) == 0:

            insert_response = (
                supabase.table("Credits")
                .insert({
                    "id": user_id,
                    "credits": 0
                })
                .execute()
            )

            return {
                "message": "User created",
                "user": insert_response.data
            }

        # jezeli istnieje
        return {
            "message": "User already exists",
            "user": response.data[0]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))