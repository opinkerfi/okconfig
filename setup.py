# setup.py ###
from distutils.core import setup
import os

NAME = "okconfig"
VERSION = '1.2.2'
SHORT_DESC = "%s - Powertools to generate Nagios configuration files" % NAME
LONG_DESC = """
%s contains tools and templates for enterprise quality nagios configuration.
""" % NAME


def get_filelist(path):
    """Returns a list of all files in a given directory"""
    files = []
    directories_to_check = [path]
    while len(directories_to_check) > 0:
        current_directory = directories_to_check.pop(0)
        for i in os.listdir(current_directory):
            if i == '.gitignore':
                continue
            relative_path = current_directory + "/" + i
            if os.path.isfile(relative_path):
                files.append(relative_path)
            elif os.path.isdir(relative_path):
                directories_to_check.append(relative_path)
            else:
                print "what am i?", i
    return files

if __name__ == "__main__":
    manpath = "share/man/man1/"
    etcpath = "/etc/%s" % NAME
    etcmodpath = "/etc/%s/modules" % NAME
    initpath = "/etc/init.d/"
    logpath = "/var/log/%s/" % NAME
    varpath = "/var/lib/%s/" % NAME
    rotpath = "/etc/logrotate.d"
    datarootdir = "/usr/share/%s" % NAME
    template_files = get_filelist('usr/share/okconfig')
    data_files = map(lambda x: ("/" + os.path.dirname(x), [x]), template_files)
    data_files.append((logpath, []))
    data_files.append((rotpath, ["etc/logrotate.d/okconfig"]))
    #data_files.append(( manpath, ['docs/okconfig.1.gz'] ))
    setup(
        name='%s' % NAME,
        version=VERSION,
        author='Pall Sigurdsson',
        description=SHORT_DESC,
        long_description=LONG_DESC,
        author_email='palli@opensource.is',
        url='http://okconfig.org',
        license='GPL',
        scripts=['usr/bin/okconfig'],
        packages=['okconfig'],
        install_requires=['paramiko','pynag'],
        data_files=data_files,
    )
