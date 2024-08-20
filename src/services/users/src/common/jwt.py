import base64
import hmac
import hashlib
import json

def base64url_encode(data):
	return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64url_decode(data):
	padding = '=' * (4 - (len(data) % 4))
	return base64.urlsafe_b64decode(data + padding)

def verify_jwt(token, secret):
    header_b64, payload_b64, signature_b64 = token.split('.')
    
    # header = json.loads(base64url_decode(header_b64))
    payload = json.loads(base64url_decode(payload_b64))
    
    signature_check = hmac.new(secret, f"{header_b64}.{payload_b64}".encode('utf-8'), hashlib.sha256).digest()
    signature_check_b64 = base64url_encode(signature_check)
    
    if signature_b64 != signature_check_b64:
        raise ValueError("Invalid signature")
    
    return payload
