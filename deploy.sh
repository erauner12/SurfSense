#!/usr/bin/env bash
set -euo pipefail
###############################################################################
# 2) Ensure we have a buildx builder called "multi" and switch to it
###############################################################################
docker buildx create --name multi --use 2>/dev/null || docker buildx use multi

###############################################################################
# 3) Pick the tag that both images should share
###############################################################################
VERSION="v0.1.6"                 # <── bump this when you want a new release
# If you still want the commit hash as a *third* tag, uncomment the next line.
# SHA=$(git rev-parse --short HEAD)

###############################################################################
# 4) Build & push the **UI** image
###############################################################################
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --build-arg NEXT_PUBLIC_FASTAPI_BACKEND_URL=https://surf-api.erauner.dev \
  --build-arg NEXT_PUBLIC_FASTAPI_BACKEND_AUTH_TYPE=LOCAL \
  --build-arg NEXT_PUBLIC_ETL_SERVICE=LLAMACLOUD \
  --build-arg NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID=${GOOGLE_OAUTH_CLIENT_ID:-} \
  --build-arg NEXT_PUBLIC_API_URL=https://surf-api.erauner.dev \
  -f surfsense_web/Dockerfile \
  -t ghcr.io/erauner12/surfsense_ui:latest \
  -t ghcr.io/erauner12/surfsense_ui:${VERSION} \
  --push \
  surfsense_web

###############################################################################
# 5) Build & push the **backend** image
###############################################################################
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f surfsense_backend/Dockerfile \
  -t ghcr.io/erauner12/surfsense_backend:latest \
  -t ghcr.io/erauner12/surfsense_backend:${VERSION} \
  --push \
  surfsense_backend
