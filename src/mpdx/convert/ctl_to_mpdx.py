class CtLtoMpdxConverter:
    def convert(self, ctl: CanonicalTableLayout) -> MpdxDocument:
        """
        Convert a CanonicalTableLayout into an MPDX document.
        Each original cell becomes a semantic text node (`t`).
        Layout information is stored in node.meta.
        """
        pass

