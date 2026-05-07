from supabase import create_client
import os
from dotenv import load_dotenv
import bcrypt


class AuthService:

    def __init__(self):
        load_dotenv()

        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")

        self.supabase = create_client(self.url, self.key)

    def __hash_password(self, password: str):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def __verify_password(self, password: str, hashed: str):
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def register(self, username, email, password):

        hashed_password = self.__hash_password(password)

        data = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "premium": False
        }

        response = self.supabase.table("users").insert(data).execute()

        return response

    def login(self, email, password):

        response = (
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

        if self.__verify_password(password, user["password"]):
            return True

        return False