#!/bin/sh
# Use this script to release a new version of okconfig

current_version=$(grep ^Version: okconfig.spec | awk '{ print $2 }')
current_release=$(grep "define release" okconfig.spec | awk '{ print $3 }')

echo    "Current version is: $current_version"
echo -n "New version number: "
read new_version

echo new version: $new_version


echo "### Updating version number"
sed -i "s/Version: $current_version/Version: $new_version/" okconfig.spec
sed -i "s/__version__=.*/__version__='${new_version}'/" okconfig/__init__.py
sed -i "s/VERSION =.*/VERSION ='${new_version}'/" okconfig/__init__.py
echo "${new_version}-${current_release} /" > rel-eng/packages/okconfig

# Comment out because there is no debian package yet
# dch -v "${new_version}" --distribution unstable "New Upstream release"

echo "### commiting and tagging current git repo"
git commit okconfig/__init__.py rel-eng/packages/okconfig okconfig.spec -m "Bumped version number to $new_version" > /dev/null
git tag okconfig-${new_version}-${current_release} -a -m "Bumped version number to $new_version" 

# The following 2 require access to git repositories and pypi
echo "### Pushing commit to github"
git push origin master || exit 1
git push --tags origin master || exit 1
echo "Building package and uploading to pypi"
#python setup.py build sdist upload || exit 1
