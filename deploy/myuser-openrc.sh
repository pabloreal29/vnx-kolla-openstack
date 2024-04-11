# export OS_USERNAME=cnvr
# export OS_PASSWORD=xxxx
# export OS_PROJECT_NAME=admin
# export OS_USER_DOMAIN_NAME=Default
# export OS_PROJECT_DOMAIN_NAME=Default
# export OS_AUTH_URL=http://controller:5000/v3
# export OS_AUTH_URL=http://10.0.0.11:5000/v3
# export OS_IDENTITY_API_VERSION=3
# export OS_IMAGE_API_VERSION=2
# #export OS_AUTH_TYPE=password


# Ansible managed

# Clear any old environment that may conflict.
for key in $( set | awk '{FS="="}  /^OS_/ {print $1}' ); do unset $key ; done
export OS_PROJECT_DOMAIN_NAME='Default'
export OS_USER_DOMAIN_NAME='Default'
export OS_PROJECT_NAME='admin'
export OS_TENANT_NAME='admin'
export OS_USERNAME='myuser'
export OS_PASSWORD='xxxx'
export OS_AUTH_URL='http://10.0.0.250:5000'
export OS_INTERFACE='internal'
export OS_ENDPOINT_TYPE='internalURL'
export OS_IDENTITY_API_VERSION='3'
export OS_REGION_NAME='RegionOne'
export OS_AUTH_PLUGIN='password'
