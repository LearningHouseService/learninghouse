#!/bin/bash -x

set -euo pipefail

NEW_USER_ID=${USER_ID}
NEW_GROUP_ID=${GROUP_ID:-$NEW_USER_ID}

echo "Starting with learninghouse user id: $NEW_USER_ID and group id: $NEW_GROUP_ID"
if ! id -u learninghouse >/dev/null 2>&1; then
  if [ -z "$(getent group $NEW_GROUP_ID)" ]; then
    echo "Create group lshs with id ${NEW_GROUP_ID}"
    groupadd -g $NEW_GROUP_ID learninghouse
  else
    group_name=$(getent group $NEW_GROUP_ID | cut -d: -f1)
    echo "Rename group $group_name to learninghouse"
    groupmod --new-name learninghouse $group_name
  fi
  echo "Create user lshs with id ${NEW_USER_ID}"
  adduser -u $NEW_USER_ID --disabled-password --gecos '' --home "${LHS_HOME}" --gid $NEW_GROUP_ID learninghouse
fi

chown -R learninghouse:learninghouse "${LHS_HOME}"
sync

exec "$@"
