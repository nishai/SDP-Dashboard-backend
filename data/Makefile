
all:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean-data to clean runtime data"

clean-data:
	@echo "[Cleaning: ./data]"
	@find ./* -not -name "README.md" -a -not -name ".gitignore" -a -not -name "Makefile" -exec rm -rf {} \; || true
