.PHONY: all generate validate clean

all: generate validate

generate:
	python3 src/dice_family.py

validate:
	python3 src/repair_validate_stl.py

clean:
	rm -f step/*.step stl/*.stl
