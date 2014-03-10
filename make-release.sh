#!/bin/bash
# This script updates the version number in the manifest file,
# commits and tags the changes and then exports a ZIP
# archive of the new version

VERSION_NUMBER=$1
VERSION_DESC=$2

while [[ "" == $VERSION_NUMBER ]]; do
    echo -n "Please enter the version number: "
    read VERSION_NUMBER
    
    if $(git tag | grep -q "^v${VERSION_NUMBER}$"); then
        echo "Version '${VERSION_NUMBER}' already exists, please choose another or exit with Ctrl+C." >&2
        VERSION_NUMBER=""
    fi
done

while [[ "" == $VERSION_DESC ]]; do
    echo -n "Please enter a description for the release (e.g. 'bugfix release'): "
    read VERSION_DESC
done

echo -n "Updating manifest file to version '${VERSION_NUMBER}' and committing changes. Continue? [y/N] "
read response

if [[ "y" != $response ]] && [[ "Y" != $response ]]; then
    echo "Exiting without changes."
    exit
fi

# Update manifest
echo "Stashing working directory..."
git stash
echo "Updating manifest..."
manifest=$(< addon.xml)
echo "$manifest" | sed 's/ name="Massengeschmack" version="[^"]\+" / name="Massengeschmack" version="'"${VERSION_NUMBER}"'" /' > addon.xml

# Commit and tag changes
echo "Committing changes..."
git add addon.xml
git commit -m "Bumping version number to ${VERSION_NUMBER}"

echo "Tagging release..."
git tag -a "v${VERSION_NUMBER}" -m "Version ${VERSION_NUMBER} (${VERSION_DESC})"

echo "Re-applying and popping stash..."
git stash pop

# Export ZIP file
filename="plugin.video.massengeschmack-${VERSION_NUMBER}.zip"
echo "Exporting release to '${filename}'..."
if [ -e "${filename}" ]; then
    echo -n "File '${filename}' already exists. Overwrite? [y/N] "
    read response
    if [[ "y" != $response ]] && [[ "Y" != $response ]]; then
        echo "Exiting without changes."
        exit
    fi
fi

git archive --output="plugin.video.massengeschmack-${VERSION_NUMBER}.zip" --format=zip --prefix="plugin.video.massengeschmack/" "v${VERSION_NUMBER}"

echo "Done."