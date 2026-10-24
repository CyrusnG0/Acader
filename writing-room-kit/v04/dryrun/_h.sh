# helpers for hand-driven dry runs (student-visible output only)
R(){ python3 v04/room.py "$@"; }
S(){ echo; echo "STUDENT> $*"; R say "$SESS" "$*"; }
SP(){ echo; echo "STUDENT> (pick $1) $2"; R pick "$SESS" "$1" --reason "$2"; }
SR(){ echo; echo "STUDENT> (read $1)"; R read "$SESS" "$1"; }
SC(){ echo; echo "STUDENT> (confident) $*"; R confident "$SESS" "$*"; }
