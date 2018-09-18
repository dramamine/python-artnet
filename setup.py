from distutils.core import setup

setup(
	name = "python-artnet",
	version = "0.2",

	package_dir={'artnet': 'src/artnet'},
  packages=['artnet'],
	# entry_points={
	# 	# 'setuptools.file_finders'	: [
	# 	# 	'git = setuptools_git:gitlsfiles',
	# 	# ],
	# 	# 'console_scripts': [
	# 	# 	'artnet = artnet.scripts:main',
	# 	# ]
	# },

	#install_requires = open('requirements.txt', 'rU')
)