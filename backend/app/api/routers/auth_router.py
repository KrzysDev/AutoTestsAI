from fastapi import APIRouter, HTTPException
import os

from supabase import Client, create_client
from backend.app.models.schemas import CheckUsersTableRequest

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

router = APIRouter()

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)


@router.post("/v1/auth/check_account_table")
def check_account_table(request: CheckUsersTableRequest):

    try:
        response = (
            supabase.table("Account")
            .select("*")
            .eq("email", request.email)
            .execute()
        )

        if len(response.data) == 0:

            insert_response = (
                supabase.table("Account")
                .insert({
                    "email": request.email,
                    "credits": 3
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