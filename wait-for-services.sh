#!/bin/bash
# wait-for-services.sh

set -e

host="$1"
shift
cmd="$@"

until pg_isready -h "$host" -q -U postgres; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

until nc -z rabbit 5672; do
  >&2 echo "Rabbit is unreachable - sleeping"
  sleep 1
done

>&2 echo "All dependant services are up - executing command"
exec $cmd
