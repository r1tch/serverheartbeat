#!/bin/bash

if [ "x$1" = "x-h" ]
then
   echo usage: $0 executable_name
   echo This will create / update a packaged executable from the current directory
   echo The only requirement is to have an existing and functional __main__.py
   exit 1
fi

if [ "x$1" != "x" ]
then
  binary="$1"
else
  pwd=`pwd`
  binary=`basename $pwd`
fi


if [ ! -f __main__.py ]
then
   echo __main__.py required to run the application
   exit 1
fi



rm -f "$binary"

# copy the shebang (take existence in __main__.py for granted)
head -1 __main__.py > "$binary"

zip -r temp.zip . -i \*.py 
cat temp.zip >> "$binary"
rm temp.zip

chmod +x "$binary"


