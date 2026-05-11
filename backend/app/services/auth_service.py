from supabase import create_client, create_async_client, AsyncClient
import os
from dotenv import load_dotenv
import bcrypt


class AuthService:

    def __init__(self):
        load_dotenv()

        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")

        # Note: Using AsyncClient for async support
        self.supabase: AsyncClient = AsyncClient(self.url, self.key)

    def __hash_password(self, password: str):
        # bcrypt is blocking, but for password hashing it's usually acceptable 
        # unless it's a very high-load system.
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def __verify_password(self, password: str, hashed: str):
        return bcrypt.checkpw(password.encode(), hashed.encode())

    async def register(self, username, email, password):
        from fastapi.concurrency import run_in_threadpool
        hashed_password = await run_in_threadpool(self.__hash_password, password)

        data = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "premium": False
        }

        response = await self.supabase.table("Users").insert(data).execute()

        return response

    async def login(self, email, password):

        response = await (
            self.supabase
            .table("Users")
            .select("*")
            .eq("email", email)
            .execute()
        )

        users = response.data

        if len(users) == 0:
            return False

        user = users[0]

        from fastapi.concurrency import run_in_threadpool
        if await run_in_threadpool(self.__verify_password, password, user["password"]):
            return True

        return False