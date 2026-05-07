from backend.app.services.auth_service import AuthService


service = AuthService()

print(service.login("handsome.christopher@gmail.com", "Dupa123"))
print(service.register("Christopher","handsome.christopher@gmail.com", "Dupa123"))
print(service.login("handsome.christopher@gmail.com", "Dupa123"))