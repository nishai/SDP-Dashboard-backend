# script for deleting empty log files from all log directories
for dir in $(ls -d */)
do
	find $dir -empty -type f -delete
done
