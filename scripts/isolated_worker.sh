#!/usr/bin/env bash
# Must run as root inside a NEW mount namespace; no global mounts are changed.
set -euo pipefail
cd /
mount --make-rprivate /
mount -t tmpfs tmpfs /mnt
mount -t tmpfs tmpfs /home/nigel/acl2027/vendor/TimelyRAG
mount -t tmpfs tmpfs /home/nigel/acl2027/vendor/TimelyRAG-repaired/datasets
mount --bind /dev/null /home/nigel/acl2027/vendor/TimelyRAG-repaired/.git
mount --bind /dev/null /home/nigel/acl2027/vendor/TimelyRAG-repaired/datasets.zip
mount -t tmpfs tmpfs /home/nigel/acl2027/results
if [[ -d /home/nigel/acl2027/data ]]; then
  mount -t tmpfs tmpfs /home/nigel/acl2027/data
fi
exec runuser -u acl-infer -- env PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 /home/nigel/miniforge3/envs/timelyrag-repaired/bin/python /home/nigel/acl2027/scripts/baseline_isolated.py worker "$@"
