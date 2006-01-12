from setuptools import setup #, find_packages

setup(
	name = "Rat",
	description = "Rat is a library for simplifying common tasks of PyGtk and gnome-python",
	version = "0.1",
	author = "Tiago Cogumbreiro",
	author_email = "cogumbreiro@users.sf.net",
    url = "http://developer.berlios.de/projects/python-rat/",
    download_url = "http://developer.berlios.de/project/showfiles.php?group_id=5061",
    license = "MIT",
    # Source files are in the 'src' directory
	package_dir = {"": "src"},
	packages = ["rat"],
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT/X Consortium License",
        "Natural Language :: English",
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Environment :: X11 Applications :: Gnome",
        "Intended Audience :: Developers",
        "Topic :: Desktop Environment :: Gnome",
        "Topic :: Software Develop :: User Interfaces",
    ],
)
