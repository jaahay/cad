UV ?= uv
PROJECT ?=
BLUEPRINT ?=

.PHONY: all sync list build build-all validate validate-all test dice dice-list dice-all clean

all: test build-all validate-all

sync:
	$(UV) sync

list:
	$(UV) run python tools/export_project.py --list

build:
	@test -n "$(PROJECT)" || (echo "PROJECT is required" >&2; exit 2)
	$(UV) run python tools/export_project.py $(PROJECT) $(if $(BLUEPRINT),--blueprint $(BLUEPRINT),)

build-all:
	$(UV) run python tools/export_project.py --all

validate:
	@test -n "$(PROJECT)" || (echo "PROJECT is required" >&2; exit 2)
	$(UV) run python tools/validate_mesh.py build/$(PROJECT)$(if $(BLUEPRINT),/$(BLUEPRINT),)

validate-all:
	$(UV) run python tools/validate_mesh.py build

test:
	$(UV) run pytest

dice:
	$(UV) run python tools/tactile_dice.py

dice-list:
	$(UV) run python tools/tactile_dice.py --list

dice-all:
	$(UV) run python tools/tactile_dice.py --all

clean:
	rm -rf build
