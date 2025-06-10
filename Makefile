# ---------- image names ----------
OWNER          ?= erauner12
SHORT_SHA      := $(shell git rev-parse --short HEAD)

BACKEND_IMAGE  := ghcr.io/$(OWNER)/surfsense_backend
UI_IMAGE       := ghcr.io/$(OWNER)/surfsense_ui

# ---------- Buildx target ----------
define buildx =
	docker buildx build \
		--builder multi \      # configurable: see docs/build.md
		--pull \
		--platform linux/amd64,linux/arm64 \
		-f $1/Dockerfile \
		-t $2:$(SHORT_SHA) \
		--push \
		$1
endef

.PHONY: backend-image ui-image \
		backend-dev ui-dev dev-images \
		push-all

backend-image:
	$(call buildx,surfsense_backend,$(BACKEND_IMAGE))

ui-image:
	$(call buildx,surfsense_web,$(UI_IMAGE))

# ---------- Local dev images ----------
PLATFORMS     ?= linux/amd64   # single-arch is faster for local
BUILDER       ?= multi         # must exist; same as existing targets
LOAD_FLAG     ?= --load        # so the image is imported into docker

define buildx-local =
	docker buildx build \
		--builder $(BUILDER) \
		--platform $(PLATFORMS) \
		-f $1/Dockerfile \
		-t $2:$(TAG) \
		$(LOAD_FLAG) \
		$1
endef

backend-dev:
	$(call buildx-local,surfsense_backend,surfsense_backend)

ui-dev:
	$(call buildx-local,surfsense_web,surfsense_ui)

dev-images: backend-dev ui-dev
	@echo "✅  Local images built with tag '$(TAG)'"

# ---- Simplified remote push-all ---------------------------------
PLAT ?= linux/amd64,linux/arm64
TAG  ?= pr-$(shell date +%s)

push-all:
	docker buildx build ./surfsense_backend \
		--platform $(PLAT) \
		-t ghcr.io/$(OWNER)/surfsense_backend:$(TAG) \
		--push
	docker buildx build ./surfsense_web \
		--platform $(PLAT) \
		-t ghcr.io/$(OWNER)/surfsense_ui:$(TAG) \
		--push
	@echo "✅  Both images pushed with tag '$(TAG)'"