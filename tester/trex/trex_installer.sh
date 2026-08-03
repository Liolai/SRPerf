#!/bin/sh

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <T-REX version (e.g. 3.08) >"
    exit 1
fi

TREX_VERSION=$1
TREX_DOWNLOAD_REPO="https://trex-tgn.cisco.com/trex/release/"
TREX_DOWNLOAD_PACKAGE="v${TREX_VERSION}.tar.gz"
TREX_PACKAGE_URL="${TREX_DOWNLOAD_REPO}${TREX_DOWNLOAD_PACKAGE}"
TARGET_DIR="/opt/"
TREX_DIR="trex-core-${TREX_VERSION}"
TREX_INSTALL_DIR="${TARGET_DIR}${TREX_DIR}"

if test "$(id -u)" -ne 0
then
    echo "Please use root or sudo to be able to access target installation directory: ${TARGET_DIR}"
    exit 1
fi

WORKING_DIR=$(mktemp -d)
test $? -eq 0 || exit 1

cleanup () {
    rm -r ${WORKING_DIR}
}

trap cleanup EXIT

test -d ${TREX_INSTALL_DIR} && echo "T-REX aleready installed: ${TREX_INSTALL_DIR}" && exit 0

echo "Downloading T-REX from: ${TREX_PACKAGE_URL}"
echo "Bypassing certificate check because of missing intermediate certificates on trex-tgn.cisco.com."
wget --no-check-certificate --no-verbose --no-cache -P ${WORKING_DIR} ${TREX_PACKAGE_URL}
test $? -eq 0 || exit 1

mkdir -p ${TREX_INSTALL_DIR}
tar -xzf ${WORKING_DIR}/${TREX_DOWNLOAD_PACKAGE} -C ${TREX_INSTALL_DIR} --strip-components=1
test $? -eq 0 || exit 1

tar -xzf ${TREX_INSTALL_DIR}/trex_client_${TREX_DOWNLOAD_PACKAGE} -C ${TREX_INSTALL_DIR}

# cd ${TREX_INSTALL_DIR}/linux_dpdk/ && ./b configure && ./b build || exit 1
# cd ${TREX_INSTALL_DIR}/scripts/ko/src && make && make install || exit 1
