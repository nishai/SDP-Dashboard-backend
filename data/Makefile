
all:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean-data to clean runtime data"

clean-data:
	@echo "[Cleaning: ./data]"
	@find ./* -not -name "README.md" -a -not -name ".gitignore" -a -not -name "Makefile" -exec rm -rf {} \; || true

clean-test-data:
	@echo "[Cleaning (Tests): ./data]"
	@find ./* -not -name "README.md" -a -not -name ".gitignore" -a -not -name "Makefile" -a -not -name "db.sqlite3" -exec rm -rf {} \; || true
