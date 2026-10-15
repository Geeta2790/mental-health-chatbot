#!/bin/bash
#
# Upload every .pdf/.txt in data/ to the running WellMind AI server
# as the admin user. Reads ADMIN_EMAIL, ADMIN_PASSWORD, DOMAIN from
# .env.docker.
#
# Usage:
#   bash upload_data.sh
#
# Override target URL:
#   WELLMIND_URL=https://your-host bash upload_data.sh

set -e

if [ -f .env.docker ]; then
    set -a
    . .env.docker
    set +a
fi

URL="${WELLMIND_URL:-}"
if [ -z "$URL" ]; then
    if [ -n "$DOMAIN" ]; then
        URL="https://$DOMAIN"
    else
        URL="http://127.0.0.1:8001"
    fi
fi

if [ -z "${ADMIN_EMAIL:-}" ] || [ -z "${ADMIN_PASSWORD:-}" ]; then
    echo "ADMIN_EMAIL and ADMIN_PASSWORD must be set (usually in .env.docker)." >&2
    exit 1
fi

echo "Target:       $URL"
echo "Admin email:  $ADMIN_EMAIL"
echo

echo "Logging in..."
LOGIN_RESPONSE=$(curl -sS -X POST "$URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -oE '"access_token":"[^"]+"' \
    | sed 's/"access_token":"//;s/"$//')

if [ -z "$TOKEN" ]; then
    echo "Login failed. Server response:" >&2
    echo "$LOGIN_RESPONSE" >&2
    exit 1
fi

echo "Logged in (token length: ${#TOKEN})."
echo

shopt -s nullglob
FOUND=0

for f in data/*.pdf data/*.txt data/*.PDF data/*.TXT; do
    FOUND=1
    echo "Uploading: $f"
    curl -sS -X POST "$URL/documents/upload" \
        -H "Authorization: Bearer $TOKEN" \
        -F "file=@$f"
    echo
    echo
done

if [ "$FOUND" = "0" ]; then
    echo "No .pdf or .txt files found in data/" >&2
    exit 1
fi

echo "Current knowledge base:"
curl -sS -H "Authorization: Bearer $TOKEN" "$URL/documents/sources"
echo
