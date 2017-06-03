PACKAGE_FILE = annotations_forward-1.1.rvpkg
HOME_PACKAGE_AREA = $(HOME)/.rv/Packages
PACKAGE_PATH = $(HOME_PACKAGE_AREA)/$(PACKAGE_FILE)
SOURCES = PACKAGE \
		  annotations_forward.py

$(PACKAGE_FILE): $(SOURCES)
	@rm -f $@
	zip $@ $(SOURCES)

home_install: $(PACKAGE_FILE)
	rvpkg -force -remove $(PACKAGE_PATH)
	rvpkg -force -add $(HOME_PACKAGE_AREA) $<
	rvpkg -force -install $(PACKAGE_PATH)
	rvpkg -optin $(PACKAGE_PATH)

clean:
	rvpkg -force -remove $(PACKAGE_PATH)
	rm -f $(PACKAGE_FILE)
