#!/bin/bash
set -e
APP_NAME="my-service"
DEPLOY_DIR="/opt/$APP_NAME"
BACKUP_DIR="/var/backups/$APP_NAME"
MAX_RETRIES=3
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}
log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}
check_dependencies() {
    for cmd in curl tar systemctl; do
        if ! command -v $cmd &> /dev/null; then
            log_error "Missing dependency: $cmd"
            return 1
        fi
    done
    return 0
}
backup_current() {
    if [ -d "$DEPLOY_DIR" ]; then
        log_info "Backing up to $BACKUP_DIR/$TIMESTAMP"
        mkdir -p $BACKUP_DIR
        cp -r $DEPLOY_DIR $BACKUP_DIR/$TIMESTAMP
    fi
}
deploy_release() {
    local version=$1
    local url="https://releases.example.com/$APP_NAME/$version.tar.gz"
    log_info "Downloading version $version"
    curl -sSL -o /tmp/release.tar.gz $url
    if [ $? -ne 0 ]; then
        log_error "Download failed"
        return 1
    fi
    mkdir -p $DEPLOY_DIR
    tar -xzf /tmp/release.tar.gz -C $DEPLOY_DIR
    log_info "Deployed $version"
}
restart_service() {
    local retries=0
    while [ $retries -lt $MAX_RETRIES ]; do
        systemctl restart $APP_NAME
        if systemctl is-active --quiet $APP_NAME; then
            log_info "Service restarted successfully"
            return 0
        fi
        retries=$((retries + 1))
        sleep 2
    done
    log_error "Failed to restart after $MAX_RETRIES attempts"
    return 1
}
main() {
    local version=${1:-latest}
    log_info "Starting deployment of $APP_NAME version $version"
    check_dependencies
    if [ $? -ne 0 ]; then
        exit 1
    fi
    backup_current
    deploy_release $version
    restart_service
    log_info "Deployment complete"
}
main "$@"
if [ "$version" == "latest" ]; then
    log_info "Deployed latest version"
fi
