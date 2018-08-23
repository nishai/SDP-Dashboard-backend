from .models import *
import django.apps
import sys
import xlrd

def add_data_to_tables(titles, data):
	for _model in django.apps.apps.get_models():
		_model_fields = [f.name for f in _model._meta.get_fields()]
		for row in data:
			_model_dict = {key: value for key, value in zip(titles, row) if key in _model_fields}
			_model.objects.update_or_create(**_model_dict)

#https://stackoverflow.com/questions/26029095/python-convert-excel-to-csv#26030521
def load_excel(excel_url):
	with xlrd.open_workbook(excel_url) as workbook:
		worksheet_names = workbook.sheet_names()
		worksheets = []
		for name in worksheet_names:
			worksheets.append(workbook.sheet_by_name(name))

		all_titles = []
		all_data_lists = []
		for worksheet in worksheets:
			titles = worksheet.row_values(0)
			all_titles.append(title)

			sheet_data_list = []
			for rownum in xrange(1,worksheet.nrows):
				sheet_data_list += [worksheet.row_values(rownum)]
			all_data_lists.append(data_list)

		return all_titles, all_data_lists


def load_file(file_url):
	try:
		if file_url[-4:] == ".csv":
			table_titles, table_data = load_csv(file_url)
		elif file_url[-4:] == ".xls" or file_url[-5:] == ".xlsx":
			all_titles, all_data = load_excel(file_url)
			
			# asapt titles to snake case
			all_titles = [[col.replace(" ","_").lower() for col in sheet_title] for sheet_titles in all_titles]
			# adapt data from lists to tuples
			all_data = [[tuple(row) for row in sheet_data] for sheet_data in all_data]
		else:
			raise Exception("bad file type provided. only .csv, .xls, .xlsx accepted.")
		return all_titles, all_data
	except Exception as e:
		raise Exception("error loading data from file " + file_url + " : " + str(e))


if __name__ == "__main__":

	for file_url in sys.argv[1:]:
		try:
			# load file data
			all_titles, all_data = load_file(file_url)
		except Exception as e:
			print("Error loading files: " + str(e))
			continue

		try:
			for sheet_titles, sheet_data in zip(all_titles, all_data):
				add_data_to_tables(sheet_titles, sheet_data)
		except Exception as e:
			print("Error adding data to tables: " + str(e))

