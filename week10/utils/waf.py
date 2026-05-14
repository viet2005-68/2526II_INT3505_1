from flask import request, jsonify
import re

BLOCK_PATTERNS = [
    r"(\%27)|(\')|(\-\-)|(\%23)|(#)",  # SQLi
    r"(?i)(union|select|drop|insert|delete|update)",
    r"<script.*?>.*?</script>",        # XSS
    r"\.\./",                          # Path traversal
]

def waf_check():

    payload = str(request.get_data(as_text=True))
    query = str(request.query_string.decode())

    combined = payload + query

    for pattern in BLOCK_PATTERNS:

        if re.search(pattern, combined):

            return jsonify({
                "error": "Blocked by WAF",
                "pattern": pattern
            }), 403

    return None