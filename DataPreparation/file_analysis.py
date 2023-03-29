import glob
from xml.etree import cElementTree as ET
import xmltodict
import ast
from bs4 import BeautifulSoup
from ordered_set import OrderedSet
import os
import subprocess

class FileAnalysis:
	def get_file_content(self, file_name):
		# Read the file
		file_content = open(file_name, "r")
		file_content = file_content.read()
		return file_content

	def get_all_java_classes_methods(self, parent_directory):
		class_method_dict = {}
		java_classes = []
		for filename in sorted(glob.glob(f'{parent_directory}/**/*.java', recursive = True)):
			with open(filename) as java_file:
				java_code = java_file.read()

				#https://stackoverflow.com/questions/8659275/how-to-store-the-result-of-an-executed-shell-command-in-a-variable-in-python
				command = "srcml " + filename
				class_xml = subprocess.check_output(command, shell=True)

				xmltree = ET.fromstring(class_xml)

				#https://www.geeksforgeeks.org/reading-and-writing-xml-files-in-python/
				Bs_data = BeautifulSoup(class_xml, "xml")

				functions = Bs_data.find_all('function')

				method_body = []

				for function in functions:
					method_body.append(function.text)

				class_method_dict[filename] = method_body
			
				try:
					tree = javalang.parse.parse(java_code)  # A CompilationUnit (root of AST)
					java_classes.extend(tree.types)
					
				except:
					continue

		return class_method_dict, java_classes


	def get_filtered_files(self, parent_directory, set_of_activities):
		predicted_files = []
		
		for filename in sorted(glob.glob(f'{parent_directory}/**/*.java', recursive = True)):
			basename=os.path.basename(filename)
			basename=basename.split('.')[0]
			activity_exist = False
			for item in set_of_activities:
				if "/" in item:
					if len(item)>0 and item is not None and item + ".java" in filename:
						activity_exist = True
				else: 
					if len(item)>0 and item is not None and item==basename:
						activity_exist = True

			if activity_exist==True:
				#print(f'Matched {filename}')
				predicted_files.append(filename)

		return predicted_files

	def get_additional_files(self, parent_directory, list_of_filenames):
		predicted_files = []
		
		for filename in sorted(glob.glob(f'{parent_directory}/**/*.java', recursive = True)):
			basename=os.path.basename(filename)
			basename=basename.split('.')[0]
			activity_exist = False
			for item in list_of_filenames:
				# if len(item)>0 and item is not None and item==basename:
				#     activity_exist = True
				if "/" in item:
					if len(item)>0 and item is not None and item + ".java" in filename:
						activity_exist = True
				else: 
					if len(item)>0 and item is not None and item==basename:
						activity_exist = True

			if activity_exist==True:
				predicted_files.append(filename)

		return predicted_files

	def get_all_java_files(self, parent_directory):
		all_files = []
		
		for filename in sorted(glob.glob(f'{parent_directory}/**/*.java', recursive = True)):
			all_files.append(filename)

		return all_files

	def get_string_ids(self, parent_directory, keyword):
		string_ids = []
		for filename in sorted(glob.glob(f'{parent_directory}/**/strings.xml', recursive = True)):
			#print(filename)
			with open(filename) as xml_file:
				xml_data = xml_file.read()
				Bs_data = BeautifulSoup(xml_data, "xml")
				#print(Bs_data)
				strings = Bs_data.find_all('string')
				#print(strings)
				for string in strings:
					if string.text == keyword:
						string_ids.append(string['name']) 
		
		return string_ids

	def get_android_ids(self, parent_directory, keyword):
		android_ids = []
		for filename in sorted(glob.glob(f'{parent_directory}/**/*.xml', recursive = True)):
			if 'strings.xml' in filename:
				continue
			#print(filename)
			with open(filename) as xml_file:
				xml_data = xml_file.read()
				soup = BeautifulSoup(xml_data, "xml")
				#print(Bs_data)
				sections = soup.find_all(True)
				#print(strings)
				for string in sections:
					if string.has_attr('android:text'):
						if keyword in string['android:text']:
							if string.has_attr('android:id'):
								android_id = string['android:id'].split('/')[1]
								android_ids.append(android_id)
								# print('a')
								# print(android_id)
					# if string.text == keyword:
					#     string_ids.append(string['name']) 
		
		return android_ids

	def get_start_methods(self, graph_dict, called_method_dict, predicted_files):
		list_of_start_methods = []
		for java_class in graph_dict:
			match_class_flag = False
			for predicted_file in predicted_files:
				if java_class in predicted_file:
					match_class_flag = True

			if match_class_flag==True:
				callee_methods = called_method_dict[java_class]
				list_of_start_methods.extend(callee_methods)
		return list_of_start_methods

	def get_filenames_based_on_imports(self, predicted_activity_files):
		filenames = []
		for activity_file in predicted_activity_files:
			#https://stackoverflow.com/questions/8659275/how-to-store-the-result-of-an-executed-shell-command-in-a-variable-in-python
			command = "srcml " + activity_file
			class_xml = subprocess.check_output(command, shell=True)

			xmltree = ET.fromstring(class_xml)

			#https://www.geeksforgeeks.org/reading-and-writing-xml-files-in-python/
			soup = BeautifulSoup(class_xml, "xml")

			imports = soup.find_all('import')
			for import_statement in imports:
				import_splits = import_statement.text.split(".")
				if len(import_splits)>0:
					found_filename = import_splits[len(import_splits)-1]
					found_filename = found_filename.split(';')[0]
					filenames.append(found_filename)
					if len(import_splits)>1:
						found_filename = import_splits[len(import_splits)-2]
						filenames.append(found_filename)

		return filenames


	# checks the source code of the files and in every method in files in a term exists 
	def get_class_other_terms(self, parent_directory, search_terms):
		class_method_list = []
		list_of_other_files = []
		for filename in sorted(glob.glob(f'{parent_directory}/**/*.java', recursive = True)):
			#https://stackoverflow.com/questions/8659275/how-to-store-the-result-of-an-executed-shell-command-in-a-variable-in-python
			command = "srcml " + filename
			class_xml = subprocess.check_output(command, shell=True)

			xmltree = ET.fromstring(class_xml)

			#https://www.geeksforgeeks.org/reading-and-writing-xml-files-in-python/
			Bs_data = BeautifulSoup(class_xml, "xml")

			functions = Bs_data.find_all('function')

			for function in functions:
				search_terms = [term.lower() for term in search_terms]
				search_term_exist = self.check_if_term_exist(search_terms, function.text.lower())
				if search_term_exist == True:
					class_method_list.append(function.text)
					list_of_other_files.append(filename)

		return list_of_other_files, class_method_list

	# retrieve files where any search term exists
	def get_files_if_term_exists(self, parent_directory, search_terms):
		list_of_matched_files = []
		for filename in sorted(glob.glob(f'{parent_directory}/**/*.java', recursive = True)):
			file_content = self.get_file_content(filename)

			#search_terms = [term.lower() for term in search_terms]
			search_term_exist = self.check_if_term_exist(search_terms, file_content)

			if search_term_exist == True:
				list_of_matched_files.append(filename)

		return list_of_matched_files


	def get_method_block_with_file_name(self, class_method_name, class_method_dict):
		class_method_name = class_method_name.split(".")
		class_name = class_method_name[0]
		method_name = class_method_name[1]
		method_name_parts = re.split(r"[(),]", method_name)
		method_name_parts = self.remove_empty_from_list(method_name_parts)
		method_block = ""

		for filename in class_method_dict:
			#print("class")
			#print(class_name)
			#print(filename)
			basename=os.path.basename(filename)
			basename=basename.split('.')[0]
			if class_name==basename:
				method_list = class_method_dict[filename]
				for method in method_list:
					method_full_name = method.split("{")[0]
					method_full_name_list = method_full_name.split('\n')
					if len(method_full_name_list)>0:
						method_full_name = method_full_name_list[len(method_full_name_list)-1]

					check_flag = True
					for part in method_name_parts:
						if len(part)==0:
							continue
						if part not in method_full_name:
							check_flag = False
					if check_flag == True:
						method_block = method

						break

		return class_name, method_block

	def check_if_term_exist(self, search_terms, method_block):
		match_keyword = False
		for keyword in search_terms:
			if keyword in method_block:
				match_keyword = True

		return match_keyword
