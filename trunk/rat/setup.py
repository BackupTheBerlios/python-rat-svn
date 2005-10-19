from setuptools import setup, find_packages

setup(
	name = "Rat",
	description = "Rat is a module for simplifying common tasks of PyGtk and gnome-python",
	version = "0.1",
	author = "Tiago Cogumbreiro",
	author_email = "cogumbreiro@users.sf.net",
	package_dir = {"": "src"},
	packages = ["rat"],
)
