#!/bin/bash
RSYNC="rsync -auh --info=progress2 --exclude-from=.gitignore "
LOCAL=.
REMOTE=mrk421
HOST=cp01

case "$1" in
pull)
    $RSYNC $HOST:$REMOTE/ $LOCAL
    ;;
push)
    $RSYNC $LOCAL/ $HOST:$REMOTE
    ;;
*)
    echo "'push' or 'pull'?"
    exit 1
    ;;
esac
