# Must run first: patch SSL to avoid Windows cert store ASN1 error
import ssl
import certifi

def _patched_create_default_context(purpose=ssl.Purpose.SERVER_AUTH):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations(certifi.where())
    return ctx

_orig_create_default_context = ssl.create_default_context
ssl.create_default_context = _patched_create_default_context
