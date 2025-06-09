# Building & Publishing SurfSense Docker Images

> **TL;DR**
> ```bash
> # one-time
> docker buildx create --use --name multi
>
> # backend
> make backend-image
>
> # UI
> make ui-image
> ```

## 1. Prerequisites
* Docker ≥ 24.0 with BuildKit
* `buildx` plugin (ships with Docker Desktop and docker-ce on Linux)
* GHCR write access (`echo $CR_PAT | docker login ghcr.io -u <user> --password-stdin`)

## 2. Clearing a poisoned APT cache
If you ever see
`E: Could not get lock /var/cache/apt/archives/lock`
run
```bash
docker buildx prune --builder multi --filter type=cache --force
```

## 3. Full commands (copy-paste)
```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -f surfsense_backend/Dockerfile \
  -t ghcr.io/erauner12/surfsense_backend:latest \
  -t ghcr.io/erauner12/surfsense_backend:$(git rev-parse --short HEAD) \
  --push surfsense_backend
# …same pattern for surfsense_web…
```

## 4. Note: pnpm is now available in the runtime image

The Dockerfile for `surfsense_web` now enables Corepack and activates pnpm in the runtime stage.
You do **not** need to manually install pnpm in your container or change the entrypoint –
`CMD ["pnpm", "start"]` works out of the box.

---


```
#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# 1) Authenticate once per shell (fail fast if $CR_PAT is missing / empty)
###############################################################################
: "${CR_PAT:?Environment variable CR_PAT must contain your GHCR PAT}"

echo -n "$CR_PAT" | \
  docker login ghcr.io -u erauner12 --password-stdin

###############################################################################
# 2) Ensure we have a buildx builder called “multi” and switch to it
###############################################################################
docker buildx create --name multi --use 2>/dev/null || docker buildx use multi

###############################################################################
# 3) Pick the tag that both images should share
###############################################################################
VERSION="v0.1.2"                 # <── bump this when you want a new release
# If you still want the commit hash as a *third* tag, uncomment the next line.
# SHA=$(git rev-parse --short HEAD)

###############################################################################
# 4) Build & push the **UI** image
###############################################################################
docker buildx build \
  --platform linux/amd64,linux/arm64 \
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
###############################################################################
# 6) Done!
```
