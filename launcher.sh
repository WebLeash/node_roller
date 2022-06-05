#!/usr/bin/env bash

# Launcher of the poetry virt env
#runnner with creds.
# Bring into play the AWS Keys

export BASE_DIR="/builds/insaas/tools/insaas-ami-build"


export AWS_DEFAULT_REGION="eu-west-2" # Chane to eu-west-1 for ROI

show_help() {
cat << EOF
Usage: ${0##*/}  -e ENVIRONMENT
only using development currently. NOT set-up for Production

EOF
}


while getopts "e:" opt; do
    case "$opt" in

        e)  ENV=$OPTARG # Only coded for Development. 
            ;;
        *)
            show_help >&2
            exit 1
            ;;
    esac
done

if [[ -z "$ENV" ]]; then
       show_help >&2
       exit 1
fi

# Select statement logic here to apply different accounts for the kubeconfig

vault ()
{
    echo "Vault not white listed NO CONNECTION"; return
    export VAULT_ADDR=https://vault.secrets.digital.coveahosted.co.uk
    export VAULT_TOKEN=""

    if [[ "${VAULT_TOKEN:-}" == "" ]]; then
       echo "Vault token is not set"
       exit 1
    fi
    QUERY="ci-insaas-dev/platform/test-nathan"
    ./vault kv get -field=kubeconfig "${QUERY}" >/code/.kube/kubeconfig


}

config (){
    echo "Generating kubeconfig"
    mkdir -p ${BASE_DIR}/.kube
    cat ${insaas_box_config} >${BASE_DIR}/.kube/kubeconfig
    export KUBECONFIG=${BASE_DIR}/.kube/kubeconfig 
    echo "Setting up AWS Keys...."
    export AWS_ACCESS_KEY_ID=${INSAAS_DEV_BUILD_KEY}
    export AWS_SECRET_ACCESS_KEY=${INSAAS_DEV_BUILD_SECRET_KEY}


       
}


main(){
    #vault #
    config
    cd roller 
    poetry config virtualenvs.create false 
    poetry install --no-interaction --no-ansi
    poetry run python roller/__main__.py
    exit 0
}


main


