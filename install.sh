#!/bin/bash
_CONTINUE () {
    #Ask to continue
    echo "This will install the latest version of timekpr,"
    read -p "is this what you want to do? [Y]/n: " CHOICE
    if [ "$CHOICE" = "y" ] || [ "$CHOICE" = "Y" ] || [ "$CHOICE" = "" ] ; then
        _COPYSTUFF
    elif [ "$CHOICE" = "n" ]; then
        echo "You have chosen not to continue. Exiting..."
        exit 1
    else
        echo ""
        echo "Invalid selection! Try again."
        echo ""
        _CONTINUE
    fi
}

_COPYSTUFF() {
    cat debian/install | while read a b; do
        echo "Copy $a to $b"
        cp $a /$b
    done
    echo ""
    echo "timekpr has been updated!"
    echo "Please report any bugs at http://bugs.launchpad.net/timekpr"
    echo ""
}

echo ""
_CONTINUE
echo ""

