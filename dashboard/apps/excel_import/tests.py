from django.test import TestCase
from excel_import.management.commands  import Command

class ExcelImportTestCase(TestCase):
	command = Command.Command()
	def setUp(self):
		pass

	def test_specific_excel():
		command.handler(options=['asd'])
		pass


	def test_all_excel():
		command.handler(options=[])
		pass
