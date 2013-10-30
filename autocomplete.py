import sublime, sublime_plugin
import os
import re
from threading import Thread


class SassAutocomplete(sublime_plugin.EventListener):

	def on_query_completions(self, view, prefix, locations):
		if ".scss" not in sublime.active_window().active_view().file_name():
			return
		if 0 == len(MainIndex.index) and not Indexer.is_running:
			Indexer().start()
			return []

		return MainIndex.index

	def on_post_save_async(self, view):
		if ".scss" in view.file_name():
			Indexer().start()


class MainIndex(object):
	index = []


class Indexer(Thread):
	is_running = False
	def run(self):
		MainIndex.index = []
		Indexer.is_running = True
		root_folder = sublime.active_window().folders()[0] + "/"
		files = self.read_folder(root_folder)

		for file_name in files:
			if ".scss" in file_name:
				content = open(file_name, "r").read()
				# print(content)
				matches = list(set(re.findall("\$[\w\-\d]+", content)))
				for match in matches:
					# match = match[0:len(match)]
					MainIndex.index.append(
						(
							match,
							match.replace("$", "\$"))
					)
		MainIndex.index.sort()
		MainIndex.index = list(set(MainIndex.index))

		Indexer.is_running = False

	def read_folder(self, folder):
		files = []
		for file_name in os.listdir(folder):
			if "." != file_name and ".." != file_name and os.path.isdir(folder + file_name):
				# print("trye read " + folder + file_name)
				files = files + self.read_folder(folder + file_name + "/")
			else:
				if ".scss" in file_name:
					files.append(folder + file_name)
		return files
