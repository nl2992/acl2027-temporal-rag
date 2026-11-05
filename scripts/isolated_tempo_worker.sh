#!/usr/bin/env bash
set -euo pipefail
cd /
mount --make-rprivate /
mount -t tmpfs tmpfs /mnt
mount -t tmpfs tmpfs /home/nigel/acl2027/vendor/TimelyRAG
mount -t tmpfs tmpfs /home/nigel/acl2027/vendor/TimelyRAG-repaired/datasets
mount --bind /dev/null /home/nigel/acl2027/vendor/TimelyRAG-repaired/.git
mount --bind /dev/null /home/nigel/acl2027/vendor/TimelyRAG-repaired/datasets.zip
mount -t tmpfs tmpfs /home/nigel/acl2027/results
mount -t tmpfs tmpfs /home/nigel/acl2027/tempo-private
if [[ -d /home/nigel/acl2027/data ]]; then
  mount -t tmpfs tmpfs /home/nigel/acl2027/data
fi
exec runuser -u acl-infer -- env PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 /home/nigel/miniforge3/envs/tempo-native/bin/python /home/nigel/acl2027/scripts/tempo_isolated.py worker "$@"
