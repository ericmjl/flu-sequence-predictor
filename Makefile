IMGDIR := images/

PDFIMG = $(wildcard images/*.pdf)
JPG = $(patsubst images/%.pdf, images/%.jpg, $(PDFIMG))
JPG_SMALL = $(patsubst images/%.pdf, images/%-sm.jpg, $(PDFIMG))

all: $(JPG) $(JPG_SMALL)

# Make JPG versions of images.
images/%.jpg: images/%.pdf Makefile
	convert -density 300 $< -quality 100 -alpha on $@

# Make small JPG versions of images
images/%-sm.jpg: images/%.pdf Makefile
	convert -density 200 $< -quality 100 -alpha on $@
