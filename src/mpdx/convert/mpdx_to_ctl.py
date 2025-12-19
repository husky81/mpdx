

class MpdxToCtlConverter:
    def convert(self, doc: MpdxDocument) -> CanonicalTableLayout:
        """
        Reconstruct CanonicalTableLayout from MPDX layout metadata.
        Requires layout-preserving MPDX (v0).
        """
