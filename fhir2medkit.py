# pip install medkit-lib fhir.resources pdfminer.six requests
from base64 import b64decode
from typing import Tuple, Optional
import json
import io
import requests

from fhir.resources.documentreference import DocumentReference
from medkit.core.text import TextDocument

# ---- helpers ---------------------------------------------------------------

TEXT_MIME_PREFIXES = ("text/",)
PDF_MIME = "application/pdf"

def _get_attachment(dr: DocumentReference):
    if not dr.content:
        raise ValueError("DocumentReference.content is empty")
    # pick the first available attachment; adapt if you need more complex selection
    att = dr.content[0].attachment
    if att is None:
        raise ValueError("No attachment found in first content entry")
    return att

def _resolve_bytes_and_ct(att) -> Tuple[bytes, str]:
    """
    Return (data_bytes, content_type) from Attachment using either inline data or url.
    """
    ct = att.contentType or "application/octet-stream"
    if att.data is not None:
        # FHIR library already decodes base64 data automatically
        if isinstance(att.data, bytes):
            return att.data, ct
        else:
            return b64decode(att.data), ct

    if att.url:
        # Handle file:// URLs for local files
        if att.url.startswith("file://"):
            file_path = att.url[7:]  # Remove "file://" prefix
            with open(file_path, 'rb') as f:
                return f.read(), ct
        else:
            # NOTE: If URL is a FHIR Binary endpoint, you may need auth headers here.
            resp = requests.get(att.url)
            resp.raise_for_status()
            # Prefer HTTP header content-type if present
            return resp.content, resp.headers.get("Content-Type", ct)

    raise ValueError("Attachment has neither data nor url")

def _extract_text_from_pdf(pdf_bytes: bytes) -> str:
    # minimal PDF text extraction with pdfminer.six
    from pdfminer.high_level import extract_text
    with io.BytesIO(pdf_bytes) as f:
        return extract_text(f) or ""

def _is_text_like(content_type: str) -> bool:
    return content_type.startswith(TEXT_MIME_PREFIXES)


# ---- main conversion -------------------------------------------------------

def documentreference_to_medkit(dr_json: dict):
    dr = DocumentReference.model_validate(dr_json)
    att = _get_attachment(dr)
    blob, ct = _resolve_bytes_and_ct(att)

    # Build a metadata dict from useful FHIR fields (extend as needed)
    meta = {
        "fhir_resourceType": "DocumentReference",
        "fhir_id": dr.id,
        "fhir_subject": getattr(dr.subject, "reference", None) if dr.subject else None,
        "fhir_type": dr.type.text if getattr(dr, "type", None) else None,
        "fhir_category": [c.coding[0].code if c.coding else None for c in (dr.category or [])],
        "fhir_date": dr.date.isoformat() if dr.date else None,
        "fhir_author": [a.reference for a in (dr.author or []) if getattr(a, "reference", None)],
        "fhir_custodian": getattr(dr.custodian, "reference", None) if dr.custodian else None,
        "fhir_contentType": ct,
        "fhir_size": len(blob),
        "fhir_url": getattr(att, "url", None),
        "fhir_hash": getattr(att, "hash", None),
        "fhir_language": getattr(att, "language", None),
        "fhir_title": getattr(att, "title", None),
    }

    # Route by MIME
    if _is_text_like(ct):
        # Use utf-8 encoding regardless of language setting for decoding
        text = blob.decode("utf-8", errors="replace") if ct != PDF_MIME else ""
        return TextDocument(text=text, metadata=meta)

    if ct == PDF_MIME:
        text = _extract_text_from_pdf(blob)
        return TextDocument(text=text, metadata={**meta, "extracted_from_pdf": True})


    # Fallback: treat as bytes you’ll process later; store as a “container” TextDocument with a note
    placeholder = f"[{ct} binary content; {len(blob)} bytes]"
    return TextDocument(text=placeholder, metadata={**meta, "binary_only": True})

print("Module loaded. Implement your own tests or usage below.")