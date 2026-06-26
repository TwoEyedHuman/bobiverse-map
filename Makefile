.PHONY: dev build generate docker-build docker-run docker-kill

IMAGE := bobiverse-tracker:test
CONTAINER := bobiverse-tracker
DOCKER_STAMP := .docker-build-stamp
DOCKER_SRC := Dockerfile $(shell find web/src web/static -type f) web/package.json web/package-lock.json "Bobiverse PITs - PITs.csv" csv_to_json.py

generate:
	python3 csv_to_json.py

dev:
	cd web && npm run dev

build: generate
	cd web && npm run build

$(DOCKER_STAMP): $(DOCKER_SRC)
	docker build -t $(IMAGE) .
	touch $(DOCKER_STAMP)

docker-build: $(DOCKER_STAMP)

docker-run: docker-build
	@docker run -d --rm -p 80 --name $(CONTAINER) $(IMAGE); \
	port=$$(docker port $(CONTAINER) 80/tcp | head -1 | cut -d: -f2); \
	echo "$(CONTAINER) running at http://localhost:$$port"

docker-kill:
	@docker ps -q --filter name=$(CONTAINER) | xargs -r docker kill
