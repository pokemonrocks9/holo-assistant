import json
import requests
import urllib.parse
import time    
from charactercontroller import CharacterController



class DictionarySkill(CharacterController):
	def __init__(self, connection, global_timer, google_key, callback, terms, dictionary_key):
		super().__init__(connection, global_timer, google_key, callback, terms)
		self.dictionary_key = dictionary_key


	def listen(self, heard):
		flattened_terms = [item for sublist in self.terms for item in sublist]
		dictionary_resp = self.get_definition(self.dictionary_key, heard, flattened_terms)
		if dictionary_resp[0] == -1:
			self.talk("sorry_no_info.wav")
		elif dictionary_resp[1] == 0:
			self.talk("not_a_word.wav")
		else:
			if (dictionary_resp[1] == 2):
				self.talk("found_definition.wav")
			else:
				self.talk("found_definitions.wav")
			self.synthesize_text(dictionary_resp[1])
			self.talk("latest_output.wav")

	def get_definition(self, key, text, terms):
		definition_base_url = "https://wordsapiv1.p.rapidapi.com/words/%s/definitions"
		found_word = ""
		for term in terms:
			attempt = text.partition(term)[2]
			if attempt != '':
				found_word = attempt.strip().split(" ")[0]
				continue
		if found_word == "":
			return (-1)
		else:
			full_url = definition_base_url%(found_word)
			print(full_url)
			definition_response = requests.get(full_url, \
				headers={"X-RapidAPI-Key": self.dictionary_key, "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"}, \
				verify=False)
			print(definition_response)
			if definition_response.status_code == requests.codes.ok:
				json_resp = definition_response.json()
				definitions = [(x["definition"]) for x in json_resp["definitions"]]
				if len(definitions) == 1:
					#only return the first few definitions
					return (2, definitions[:5])
				else:
					return (1, (". ").join(definitions))
			else:
				json_resp = definition_response.json()
				try:
					#special error message for non-word, but otherwise send something generic
					json_resp["message"]
					if json_resp["message"] == "word not found":
						return (0)
					else:
						return (-1)
				except:
					return (-1)
				return (-1)
		