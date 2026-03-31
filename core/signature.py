"""
Digital signature via pyHanko.
"""
from __future__ import annotations

import os
from typing import Optional

try:
    from pyhanko.sign import signers, fields
    from pyhanko.sign.fields import SigFieldSpec
    from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
    from pyhanko.sign.signers.pdf_signer import PdfSignatureMetadata
    import pyhanko.sign.signers as pyhanko_signers
    HAS_PYHANKO = True
except ImportError:
    HAS_PYHANKO = False


class SignatureEngine:
    def __init__(self) -> None:
        self._available = HAS_PYHANKO

    @property
    def is_available(self) -> bool:
        return self._available

    def sign_with_pfx(
        self,
        input_path: str,
        output_path: str,
        pfx_path: str,
        pfx_password: str,
        reason: str = "",
        location: str = "",
        contact: str = "",
        field_name: str = "Signature1",
        page: int = 0,
    ) -> None:
        """
        Sign a PDF with a PFX/P12 certificate file.
        Produces an incrementally updated PDF.
        """
        if not self._available:
            raise RuntimeError("pyHanko n'est pas installé.")

        with open(input_path, "rb") as f:
            pdf_bytes = f.read()

        from io import BytesIO
        writer = IncrementalPdfFileWriter(BytesIO(pdf_bytes))

        # Add signature field if not present
        fields.append_signature_field(
            writer,
            sig_field_spec=SigFieldSpec(
                sig_field_name=field_name,
                on_page=page,
                box=(50, 50, 300, 100),
            ),
        )

        signer = pyhanko_signers.SimpleSigner.load_pkcs12(
            pfx_path,
            passphrase=pfx_password.encode() if pfx_password else None,
        )

        meta = PdfSignatureMetadata(
            field_name=field_name,
            reason=reason or "Document signé électroniquement",
            location=location,
            contact_info=contact,
        )

        out = BytesIO()
        pyhanko_signers.sign_pdf(writer, signature_meta=meta, signer=signer, output=out)

        with open(output_path, "wb") as f:
            f.write(out.getvalue())

    def verify(self, pdf_path: str) -> list[dict]:
        """Verify signatures in a PDF. Returns list of signature info dicts."""
        if not self._available:
            return []
        try:
            from pyhanko.sign.validation import validate_pdf_signature
            from pyhanko.pdf_utils.reader import PdfFileReader

            results = []
            with open(pdf_path, "rb") as f:
                reader = PdfFileReader(f)
                sigs = reader.embedded_signatures
                for sig in sigs:
                    status = validate_pdf_signature(sig)
                    results.append({
                        "field": sig.field_name,
                        "valid": status.valid,
                        "intact": status.intact,
                        "signer": str(status.signing_cert.subject) if status.signing_cert else "Inconnu",
                        "timestamp": str(status.timestamp) if status.timestamp else "N/A",
                    })
            return results
        except Exception as e:
            return [{"error": str(e)}]
