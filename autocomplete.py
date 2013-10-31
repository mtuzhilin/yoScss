import sublime, sublime_plugin
import os
import re
from threading import Thread
import time


class ScssAutocomplete(sublime_plugin.EventListener):
	last_update = 0
	def on_query_completions(self, view, prefix, locations):

		file_name = view.file_name()
		if ".scss" not in file_name:
			return None

		indexer = Indexer()
		# сканим не раньше чем раз в n сек
		if (time.time() - ScssAutocomplete.last_update) > 4:
			print("reindex")
			indexer.update_index(file_name)
			ScssAutocomplete.last_update = time.time()

		return indexer.get_index(file_name)

class Indexer(object):
	index = []

	def get_index(self, file_name):
		return Indexer.index

	def update_index(self, file_name):
		Indexer.index = []

		self.scan_file(file_name)

	def append_to_index(self, item):

		placement = item.strip().replace("$", "\$")
		item = "scss: " + item
		tuple_item = (item, placement)

		if tuple_item not in Indexer.index:
			Indexer.index.append(tuple_item)

	def scan_file(self, file_name):
		print("scanning %s" % file_name)
		content = open(file_name, "r").read()
		#+[^:]+:[^;]+;
		matches = re.findall("\$[\w\-\d]+|\@import\s+[\'\"][^\"\']+[\'\"]", content)
		data = []
		for match in matches:
			if "@import" in match:
				child_file_name = match.replace("@import", "").replace("\"", "").replace("'", "").strip()

				if "/" != child_file_name[0:1]:
					child_file_name = os.path.dirname(file_name) + "/" + child_file_name

				child_file_name = child_file_name + ".scss"

				self.scan_file(child_file_name)
			else:
				self.append_to_index(match)

		return data
