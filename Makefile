.PHONY: help
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

download_ne_data: ## Download data from natural earth
	curl -o data/ne_110m_land.zip https://naturalearth.s3.amazonaws.com/110m_physical/ne_110m_land.zip
	unzip -o -d data/ne_110m_land data/ne_110m_land.zip
	curl -o data/ne_110m_lakes.zip https://naturalearth.s3.amazonaws.com/110m_physical/ne_110m_lakes.zip
	unzip -o -d data/ne_110m_lakes data/ne_110m_lakes.zip

setup: ## Download data and dependencies into the docker container
	docker run --rm -it --name lego-art-map-blog-post -v `pwd`:/manim manimcommunity/manim pip install -r requirements.txt

export_requirements: ## Exports the poetry requirements that can be used by pip
	poetry export > requirements.txt

shell: ## Run bash in the container
	docker run --rm -it --name lego-art-map-blog-post -v `pwd`:/manim manimcommunity/manim /bin/bash

render: ## Run the render script in the container
	docker run --rm -it --name lego-art-map-blog-post -v `pwd`:/manim manimcommunity/manim manim -qm render.py Render

render-ql:
	docker run --rm -it --name lego-art-map-blog-post -v `pwd`:/manim manimcommunity/manim manim -ql render.py Render

render-qh:
	docker run --rm -it --name lego-art-map-blog-post -v `pwd`:/manim manimcommunity/manim manim -qh render.py Render

clean: ## Remove any generated artifacts
	rm -rf media/*/partial_movie_files/*
