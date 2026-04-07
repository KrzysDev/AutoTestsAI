from backend.app.services.search_service import SearchService



service = SearchService()

print(service.get_all_by_field("Grammar Collection", "type", "grammar"))