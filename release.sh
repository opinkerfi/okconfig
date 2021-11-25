#!/bin/bash
# Use this script to release a new version of ${project_name}

# Extract current version information
project_name=$(ls *spec | sed 's/.spec$//')
current_version=$(grep ^Version: $project_name.spec | awk '{ print $2 }')
current_release=$(grep "define release" $project_name.spec | awk '{ print $3 }')

UPDATE_INFO_FILE=$(mktemp)
trap "rm -f ${UPDATE_INFO_FILE}" EXIT

if [ -z "$EDITOR" ]; then
    EDITOR=vi
fi

main() {

    update_changes || echo FAIL

    update_version_number || echo FAIL

    new_version=$(grep ^VERSION Makefile | awk '{ print $3 }')

#    update_manpage || echo FAIL

    git_commit || echo FAIL

    git_push || echo FAIL

    upload_to_pypi || echo FAIL

    echo "### All Done"
}

update_changes() {
    ask "Update Changelog?" || return 0
    ${EDITOR} CHANGES || return 1
}

upload_to_pypi() {
    ask "Upload to pypi?" || return 0
	 	echo "To build and upload to PyPI, run the following:"
	 	echo "pip install build"
		echo "pip install twine"
   	echo "python3 -m build"
		echo "twine check dist/*"
    echo "python3 -m twine upload --repository testpypi dist/*"
    echo "python3 -m twine upload dist/*"
#    python setup.py build sdist upload || return 1
}

git_push() {
    ask "Upload to github?" || return 0
    git push origin master || return 1
    git push --tags origin master || return 1
}

update_manpage() {
    ask "Update manpage?" || return 0
    ./setup.py build_man
    gzip -c < man/okconfig.1 > man/okconfig.1.gz
}

update_version_number() {
    ask "Update version number?" || return 0
    echo    "Current version is: ${current_version}"
    read -p "New version number: " new_version

    echo
    echo "### Updating Makefile"
    sed -i "s/^VERSION.*=.*/VERSION		= ${new_version}/" Makefile
    echo "### Updating setup.py"
    sed -i "s/^VERSION.*=.*/VERSION = '${new_version}'/" setup.py
    echo "### Updating ${project_name}/__init__.py"
    sed -i "s/^__version__.*/__version__ = '${new_version}'/" ${project_name}/__init__.py
    echo "### Updating ${project_name}.spec"
    sed -i "s/^Version: ${current_version}/Version: ${new_version}/" ${project_name}.spec
    echo "### Updating rel-eng/packages/${project_name}"
    echo "${new_version}-${current_release} /" > rel-eng/packages/${project_name}

    echo "### Updating debian.upstream/changelog"
    update_debian_changelog

}

update_debian_changelog() {
    DATE=$(LANG=C date -R)
    NAME=$(git config --global --get user.name)
    MAIL=$(git config --global --get user.email)
    changelog=$(mktemp)
    echo "${project_name} (${new_version}-${current_release}) unstable; urgency=low" > ${changelog}
    echo "" >> ${changelog}
    echo "  * New upstream version" >> ${changelog}
    echo "" >> ${changelog}
    echo " -- ${NAME} <${MAIL}>  ${DATE}" >> ${changelog}
    echo "" >> ${changelog}
    cat debian.upstream/changelog >> ${changelog}
    cp -f ${changelog} debian.upstream/changelog
}


git_commit() {
    ask "Commit changes to git and tag release ?" || return 0
    git commit setup.py Makefile CHANGES ${project_name}/__init__.py rel-eng/packages/${project_name} ${project_name}.spec debian.upstream/changelog -m "Bumped version number to $new_version" > /dev/null
    git tag ${project_name}-${new_version}-${current_release} -a -m "Bumped version number to $new_version"
}

ask() {
    local prompt default reply

    if [[ ${2:-} = 'Y' ]]; then
        prompt='Y/n'
        default='Y'
    elif [[ ${2:-} = 'N' ]]; then
        prompt='y/N'
        default='N'
    else
        prompt='y/n'
        default=''
    fi

    while true; do

        # Ask the question (not using "read -p" as it uses stderr not stdout)
        echo -n "$1 [$prompt] "

        # Read the answer (use /dev/tty in case stdin is redirected from somewhere else)
        read -r reply </dev/tty

        # Default?
        if [[ -z $reply ]]; then
            reply=$default
        fi

        # Check if the reply is valid
        case "$reply" in
            Y*|y*) return 0 ;;
            N*|n*) return 1 ;;
        esac

    done
}
main;

# vim: sts=4 expandtab autoindent
