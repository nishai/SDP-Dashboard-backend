
all:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean-logs to clean all .log files"
	@echo "  clean-empty to delete all empty log files"

clean-logs:
	@echo "[Cleaning: ./data]"
	@find ./*/* -type f -name "*.log" -print -exec rm -rf {} \; || true

# script for deleting empty log files from all log directories
clean-empty:
	@echo "[Cleaning: Empty .log Files]"
	@find ./*/* -empty -type f -name "*.log" -print -exec rm -rf {} \; || true
