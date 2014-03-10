#!/bin/bash
# This script updates the version number in the manifest file,
# commits and tags the changes and then exports a ZIP
# archive of the new version

VERSION_NUMBER=$1
VERSION_DESC=$2

_CLR_GREEN='\e[1;32m'
_CLR_RED='\e[1;31m'
_CLR_NONE='\e[0m'

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
    echo -e "${_CLR_RED}Exiting without changes.${_CLR_NONE}"
    exit
fi

# Update manifest
echo -e "${_CLR_GREEN}Stashing working directory...${_CLR_NONE}"
git stash
echo -e "${_CLR_GREEN}Updating manifest...${_CLR_NONE}"
manifest=$(< addon.xml)
echo "$manifest" | sed 's/ name="Massengeschmack" version="[^"]\+" / name="Massengeschmack" version="'"${VERSION_NUMBER}"'" /' > addon.xml

# Update changelog
echo "${_CLR_GREEN}Updating changelog...${_CLR_NONE}"
changelog=$(git log $(git describe --tags --abbrev=0)..HEAD --oneline -E -i --grep=" +cl$" --format=" - %s") | grep -Ev " -cl"
if [[ "" == $changelog ]]; then
    echo "${_CLR_RED}No commits marked for changelog inclusion, trying to assemble changelog automatically...${_CLR_NONE}" >&2
    changelog=$(git log $(git describe --tags --abbrev=0)..HEAD --oneline -E -i --grep="^(Add|Fix|Update|Remove) " --format=" - %s") | grep -Ev " -cl"
fi

if [[ "" == $changelog ]]; then
    echo -e "${_CLR_RED}No changelog could be generated, skipping...${_CLR_NONE}" >&2
else
    oldChangelog=$(<changelog.txt)
    newEntries=$(echo "$changelog" | sed 's/ +cl$//')
    changelog="${VERSION_NUMBER}
${changelog}

${oldChangelog}"
    echo "$changelog" > changelog.txt
fi

# Commit and tag changes
echo -e "${_CLR_GREEN}Committing changes...${_CLR_NONE}"
git add addon.xml
git commit -m "Bump version number to ${VERSION_NUMBER} -cl"

git add changelog.txt
git commit -m "Update changelog -cl"

echo -e "${_CLR_GREEN}Tagging release...${_CLR_NONE}"
git tag -a "v${VERSION_NUMBER}" -m "Version ${VERSION_NUMBER} (${VERSION_DESC})"

echo -e "${_CLR_GREEN}Re-applying and popping stash...${_CLR_NONE}"
git stash pop

# Export ZIP file
filename="plugin.video.massengeschmack-${VERSION_NUMBER}.zip"
echo -e "${_CLR_GREEN}Exporting release to '${filename}'...${_CLR_NONE}"
if [ -e "${filename}" ]; then
    echo -n "File '${filename}' already exists. Overwrite? [y/N] "
    read response
    if [[ "y" != $response ]] && [[ "Y" != $response ]]; then
        echo -e "${_CLR_RED}Exiting without changes.${_CLR_NONE}"
        exit
    fi
fi

git archive --output="plugin.video.massengeschmack-${VERSION_NUMBER}.zip" --format=zip --prefix="plugin.video.massengeschmack/" "v${VERSION_NUMBER}"

echo -e "${_CLR_GREEN}Done.${_CLR_NONE}"