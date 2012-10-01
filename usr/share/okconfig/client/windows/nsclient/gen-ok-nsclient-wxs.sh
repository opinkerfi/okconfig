#!/bin/bash
#
# Quick and Dirty script to generate a MS WiX .wxs packaging description.
# Based on this tutorial: http://wix.tramontana.co.hu/
#
# Usage:
#    gen-ok-nsclient-wxs.sh >ok-nsclient.wxs 
# 
# On Windows (install WiX):
#    candle.exe ok-nsclient.wxs
#    light.exe ok-nsclient.wixobj
#
# Should create: ok-nsclient.msi
#
PRODUCT="OK NSPlugin Add-ons"
PRODUCTURL="http://opensource.ok.is/"
COMPANY="Opin Kerfi"
COMPANYID="OpinKerfi"
VERSION="1.$(date +%y)"   # Must be <= 255.255
BUILDID="$(date +%m%d)"   # Must fit in 0-65535
ROOTDIR="datafiles"

# This should be changed if you want to be able to install two versions
# of the product at the same time.  Generate a new one with: uuidgen
PRODUCT_UUID="dbca25c7-61d4-437b-9c32-b28c1376571d"

# This should never change, it allows MSI to recognize which packages we
# are upgrading or upgradable by.
UPGRADE_UUID="e0108d26-395f-442f-a086-86a07e616d79"

cat <<tac
<?xml version='1.0' encoding='windows-1252'?>
<Wix xmlns='http://schemas.microsoft.com/wix/2006/wi'>

 <Product Language='1033' Codepage='1252'
          Name='$PRODUCT'
          Version='$VERSION.$BUILDID'
          Id='$PRODUCT_UUID'
          UpgradeCode='$UPGRADE_UUID'
          Manufacturer='$COMPANY'>

  <Package Id='*' Keywords='Installer' InstallerVersion='100' Compressed='yes'
           Description="$PRODUCT Installer"
           Comments='$PRODUCTURL'
           Manufacturer='$COMPANY'
           Languages='1033' SummaryCodepage='1252' />

  <Media Id='1' Cabinet='Contents.cab' EmbedCab='yes' DiskPrompt="CD-ROM #1" />
  <Property Id='DiskPrompt'
            Value="$PRODUCT $VERSION Installation" />

  <Directory Id='TARGETDIR' Name='SourceDir'>
   <Directory Id='ProgramFilesFolder' Name='PFiles'>
    <Directory Id='$COMPANYID' Name='$COMPANY'>
     <Directory Id='INSTALLDIR' Name='$PRODUCT $VERSION'>
tac
CLIST=$(pwd)/clist.$$
listdir() {
  local path=$1
  local indent=$2
  for thing in *; do
    id=$(echo "$path\\$thing" |perl -npe 's,[^a-zA-Z0-9],X,g')
    bn=$(basename "$thing")
    if [ -d "$thing" ]; then
      pushd "$thing" >/dev/null
      echo "$indent<Directory Id='DIR$id' Name='$bn'>"
      listdir "$path\\$thing" "$indent "
      echo "$indent</Directory>"
      popd >/dev/null
    else
      echo "${indent}<Component Id='COMP$id' Guid='$(uuidgen)'>"
      echo "${indent} <File Id='FILE$id' Name='$bn' DiskId='1' Source='$path\\$thing' KeyPath='yes' />"
      echo "${indent}</Component>"
      echo "   <ComponentRef Id='COMP$id' />" >> $CLIST
    fi
  done
}
pushd "$ROOTDIR" >/dev/null
cp /dev/null $CLIST
listdir "$ROOTDIR" "      "
popd >/dev/null
cat <<tac
     </Directory>
    </Directory>
   </Directory>
  </Directory>

  <Feature Id='Complete' Level='1'>
tac
cat $CLIST
rm -f $CLIST
cat <<tac
  </Feature>

  <CustomAction Id='ACTRunBat' FileKey='FILEdatafilesXmsiXpostinstXbatX'
                ExeCommand='' Return='asyncNoWait' />

  <InstallExecuteSequence>
   <Custom Action='ACTRunBat' After='InstallFinalize'>NOT Installed</Custom>
  </InstallExecuteSequence>

 </Product>

</Wix>
tac
