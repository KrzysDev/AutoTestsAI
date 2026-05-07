from backend.app.services.auth_service import AuthService


service = AuthService()

print(service.login("handsome.christopher@gmail.com", "Dupa123"))