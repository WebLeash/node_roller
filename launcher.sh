#!/usr/bin/env bash

# Launcher of the poetry virt env
#runnner with creds.
# Bring into play the AWS Keys

export BASE_DIR="/builds/<your build path>"


export AWS_DEFAULT_REGION="<Your default region>" # Chane to eu-west-1 for ROI

show_help() {
cat << EOF
Usage: ${0##*/}  -e ENVIRONMENT


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
    echo "Not leveraging vault, below code goes someway towards a vault integration".
    export VAULT_ADDR=<Vault domain>
    export VAULT_TOKEN=""

    if [[ "${VAULT_TOKEN:-}" == "" ]]; then
       echo "Vault token is not set"
       exit 1
    fi
    QUERY="<vault path>"
    ./vault kv get -field=kubeconfig "${QUERY}" >/code/.kube/kubeconfig


}

config (){
    echo "Generating kubeconfig"
    mkdir -p ${BASE_DIR}/.kube
    cat ${kube_config} >${BASE_DIR}/.kube/kubeconfig
    export KUBECONFIG=${BASE_DIR}/.kube/kubeconfig 
    echo "Setting up AWS Keys...."
    export AWS_ACCESS_KEY_ID=${instore file secret store}
    export AWS_SECRET_ACCESS_KEY=${secret file secret store}


       
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


