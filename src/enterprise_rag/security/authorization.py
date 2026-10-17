class AuthorizationNotConfiguredError(RuntimeError):
    pass

def authorize_document_access(*, subject_id: str, document_metadata: dict) -> bool:
    """Replace with identity-provider integration and a real document ACL policy."""
    raise AuthorizationNotConfiguredError(
        "Document-level authorization is not configured in this starter."
    )
