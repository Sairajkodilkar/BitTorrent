
APP = bittorrent-cli
BIN_LOCATION = ~/.local/bin

default:
	@echo "usage:"
	@echo "	make install 	:	install the bittorrent-cli"
	@echo "	make uninstall	:	uninstall the bittorrent-cli"

install:
	pip install
	cp $(APP) $(BIN_LOCATION)
	chmod u+x $(BIN_LOCATION)/$(APP)

uninstall:
	pip uninstall bittorrent
	rm -f $(BIN_LOCATION)/$(APP)

dev-install:
	python3 setup.py develop

dev-uninstall:
	python3 setup.py 
	setup.py develop --uninstall