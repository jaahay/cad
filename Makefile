UV ?= uv
PROJECT ?= tactile-dice

.PHONY: all sync generate validate test clean tactile-dice

all: generate validate test

sync:
	$(UV) sync

generate:
	$(UV) run python tools/export_project.py $(PROJECT)

validate:
	$(UV) run python tools/validate_mesh.py build/$(PROJECT)/stl

test:
	$(UV) run pytest

clean:
	rm -rf build

tactile-dice:
	$(MAKE) all PROJECT=tactile-dice
