## setup.py ###
from distutils.core import setup
import os

NAME = "okconfig"
VERSION = '1.0'
SHORT_DESC = "%s - Powertools to generate Nagios configuration files" % NAME
LONG_DESC = """
%s contains tools and templates for enterprise quality nagios configuration.
""" % NAME

def get_filelist(path):
	'Returns a list of all files in a given directory'
	files = []
	directories_to_check = [path]
	while len(directories_to_check) > 0:
		current_directory = directories_to_check.pop(0)
		for i in os.listdir(current_directory):
			if os.path.isfile(i): files.append(i)
			elif os.path.isdir(i): directories_to_check.append(i)
	return files

if __name__ == "__main__":
	manpath		= "share/man/man1/"
	etcpath = "/etc/%s" % NAME
	etcmodpath	= "/etc/%s/modules" % NAME
	initpath	= "/etc/init.d/"
	logpath		= "/var/log/%s/" % NAME
	varpath		= "/var/lib/%s/" % NAME
	rotpath		= "/etc/logrotate.d"
	datarootdir	= "/usr/share/%s" % NAME
	template_files = get_filelist('usr/share/okconfig')
	setup(
		name='%s' % NAME,
		version = VERSION,
		author='Pall Sigurdsson',
		description = SHORT_DESC,
		long_description = LONG_DESC,
		author_email='palli@opensource.is',
		url='http://opensource.is/okconfig',
		license='GPL',
		scripts = [
			'usr/bin/okconfig',
		],
		packages = [
			'okconfig',
		],
      	data_files = [(datarootdir, template_files ),
		],
	)
