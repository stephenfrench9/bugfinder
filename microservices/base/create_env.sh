# The virtualenv created by this script, 'env', will be incorporated into
# the 'base' docker image. The 'base' docker image will be used to
# construct docker images for all of the other micro services. These include
# 'search', 'model', 'android', 'ios', 'db', and 'db2'.

virtualenv env
source env/bin/activate
pip install -r requirements.txt
