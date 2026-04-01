from backend.app.services.ai_service import AiService

import json

def main():
    service = AiService()

    prompt = """
        	##TWOJE ZADANIE
            Twoim zadaniem jest wyciągnięcie z podanego tekstu z podręcznika słownictwa i uporządkowanie go w odpowiednim formacie.

            ##WAŻNE
            MUSISZ wydobyć ABSOLUTNIE WSZYSTKIE słówka i zwroty, jakie znajdziesz w podanym tekście. Nie pomijaj ani jednego słowa, nie używaj skrótów typu "itd", "itp". To krytyczne dla sukcesu zadania aby niczego nie pominąć!

            ##WYMAGANY FORMAT
            Twój wymagany format odpowiedzi to JSON wyglądający w następujący sposób:
                {{
                    "subject": "temat",
                    "content": "treść"
                }}

            ##WYMAGANIA ODPOWIEDNIEGO FORMATU JSON:
            - pole subject to miejsce które określa temat słownictwa. Przykłady to: "education", "place of residence", "work" czy także "private life".
            - podany temat możesz zauważyć w wysłanym ci tekście. Prawdopodobnie jest nagłówkiem.
            - Nie zwracaj uwagi na nagłówki nieodnoszące się do treści słownictwa takie jak "Lista słownictwa".
            - pole subject powinno zawierać identyczne tematy (jeśli się powtarzają). Z tego powodu:
                - jeżeli poniższa lista NIE jest pusta wykorzystaj stworzone przez ciebie już tematy i nie twórz synonimów. Np dla jeżeli na podanej liście znajduje się "nature" nie pisz "enviorement" tylko "nature".
                    Lista: pusta
            - wszystkie pola subject powinny być zapisane małymi literami w WYŁĄCZNIE języku angielskim.
            - pole content to treść słownictwa. Jego format MUSI wyglądać następująco:
                <słowo po ANGIELSKU - <tłumaczenie słowa w języku POLSKIM (z tekstu)> - <przykładowe zdanie z tym słowem w języku ANGIELSKIM (stworzone przez Ciebie)>  

            ##WYMAGANY FORMAT ODPOWIEDZI
            - Zwróć wyłącznie JSON. Nie dodawaj żadnych dodatkowych komentarzy ani tekstu. Nic nie może znaleźć się przed ani po JSONIE - zwracasz jedynie czysty JSON.
            - ignoruj śmieciowe nagłówki i znaki takie jak numery stron, podnagłówki (verbs, nouns, adjectives itp.)
            - ABSOLUTNIE NIC NIE MOZE ZNAJDOWAC SIE PRZED ANI PO JSONIE

    """

    print("wating for response....")
    answer = service.ask_ollama_cloud_with_photo(prompt, "C:\\Users\\USER\\Desktop\\Ai Test Generator Dataset-20260321T142317Z-1-001\\Ai Test Generator Dataset\\2.jpg")

    print("Model answered: ")
    print("========================================================")
    print(answer)

    with open("answer.txt", "w", encoding="utf-8") as f:
        f.write(answer)

    print("========================================================")
    print("\n")

    try:
        data = json.loads(answer)

        with open("test.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except json.JSONDecodeError as e:
        raise ValueError(f"Model returned invalid JSON: {e}")

    print(data)

if __name__ == "__main__":
    main()