class HtmlTableParser:
    def parse(self, html: str) -> CanonicalTableLayout:
        """
        Parse a single <table> element into a CanonicalTableLayout.
        Raises ValueError if no table is found.
        """

        pass

class HtmlTableRenderer:
    def render(self, ctl: CanonicalTableLayout) -> str:
        """
        Render CanonicalTableLayout back into HTML <table>.
        Uses rowspan/colspan and preserves header cells.
        """

