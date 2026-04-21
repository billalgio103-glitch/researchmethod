PYTHON  = python
DATADIR = data
BUILDDIR = build
DB      = $(BUILDDIR)/dma.db

FIGURES = \
    $(BUILDDIR)/storage_modulus_x.svg \
    $(BUILDDIR)/storage_modulus_y.svg \
    $(BUILDDIR)/storage_modulus_z.svg \
    $(BUILDDIR)/loss_modulus_x.svg \
    $(BUILDDIR)/loss_modulus_y.svg \
    $(BUILDDIR)/loss_modulus_z.svg \
    $(BUILDDIR)/tan_delta_x.svg \
    $(BUILDDIR)/tan_delta_y.svg \
    $(BUILDDIR)/tan_delta_z.svg

DATAFRAME = $(BUILDDIR)/dma_dataframe.csv
STATS     = $(BUILDDIR)/stats_results.txt

.PHONY: all clean

all: $(FIGURES) $(DATAFRAME)

$(BUILDDIR):
	mkdir -p $(BUILDDIR)

$(DB): $(DATADIR)/dma_tatas.xlsx scripts/extract.py | $(BUILDDIR)
	$(PYTHON) scripts/extract.py $(DATADIR)/dma_tatas.xlsx $(DB)

$(FIGURES): $(DB) scripts/plot.py
	$(PYTHON) scripts/plot.py $(DB) $(BUILDDIR)

$(DATAFRAME) $(STATS): $(DB) scripts/analyze.py
	$(PYTHON) scripts/analyze.py $(DB) $(BUILDDIR)

clean:
	rm -rf $(BUILDDIR)
