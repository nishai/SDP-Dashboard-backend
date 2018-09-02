
all:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean-migrations to clean migrations."

clean-migrations:
	@echo "[Cleaning: ./data]"
	@find ./* -not -name "README.md" -a -not -name ".gitignore" -a -not -name "Makefile" -a -not -name "__init__.py" -print -exec rm -rf {} \; || true
	@#find ./* -not -name "README.md" -a -not -name ".gitignore" -a -not -name "Makefile" -a -not -regex "[.]/[0-9]\{4\}.*.py" -print -exec rm -rf {} \;
