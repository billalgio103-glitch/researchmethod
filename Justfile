# DMA Materials Analysis - Reproducible Build
# Usage: just

default: build

build:
    podman compose run --rm builder make

clean:
    podman compose run --rm builder make clean

# Run without container (requires local Python + dependencies)
local:
    make
