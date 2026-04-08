from backend.app.services.search_service import SearchService


service = SearchService()


print(service.get_points_with_subject("Present Simple"))


