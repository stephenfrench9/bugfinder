#!/usr/bin/env bash
kops delete cluster --name ${NAME} --yes
sh delete_bucket.sh