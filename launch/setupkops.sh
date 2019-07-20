#!/user/bin/env bash

export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
export NAME=myfirstcluster.principledfunds.org
export KOPS_STATE_STORE=s3://$(cat bucketname.txt)
export EDITOR=emacs
