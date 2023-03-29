import re
from nltk.tokenize import wordpunct_tokenize

class Preprocess:
	def preprocess_file_content(self, file_content):
	    # Replace escape character with space
	    file_content = file_content.replace("\n", " ")

	    # Replace special characters with space
	    file_content = re.sub("[^A-Za-z0-9\s.]+", " ", file_content)

	    return file_content

	def camel_case_split(self, identifier):
	    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
	    return [m.group(0) for m in matches]

	def tokenize_file_content(self, file_content):
	    file_tokens = []

	    # Tokenize the file content by spliting it into words
	    for token in wordpunct_tokenize(file_content):
	        # This avoid having tokens like '.'
	        if (len(token) > 1) and (not token.isdigit()):
	            # split the camelCase words
	            for word in self.camel_case_split(token):
	                file_tokens.append(word.lower())

	    return file_tokens

	def get_preprocessed_data(self, contents):
	    contents_processed = self.preprocess_file_content(contents)
	    contents_tokens = self.tokenize_file_content(contents_processed)
	    contents_string = ' '.join(contents_tokens)
	    return contents_string