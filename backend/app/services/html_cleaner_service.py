from bs4 import BeautifulSoup

class HtmlCleanerService:
    """
    Service responsible for cleaning HTML before rendering (e.g. to PDF).

    Removes empty elements that can cause layout issues like:
    - empty divs / p / section
    - whitespace-only content
    - &nbsp; only nodes
    """

    EMPTY_TAGS = {"div", "p", "section"}

    def clean(self, html: str) -> str:
        """
        Cleans HTML by removing empty or whitespace-only elements.

        Args:
            html (str): Raw HTML string

        Returns:
            str: Cleaned HTML string
        """

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all():
            if tag.name in self.EMPTY_TAGS:

                # Get raw text content
                text = tag.get_text(strip=True)

                # Normalize non-breaking spaces
                text = text.replace("\xa0", "").strip()

                # If no meaningful content -> remove element
                if not text:
                    tag.decompose()

        return str(soup)