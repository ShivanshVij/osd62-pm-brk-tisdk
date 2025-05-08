#!/bin/sh
#
# osd625_brk_sdk_setup.sh
# Example: ./osd625_brk_sdk_setup.sh <PATH TO SDK ROOT>

# -------- functions --------
usage() {
    cat <<EOF
Usage: $(basename "$0") <PATH TO SDK> 

  <PATH TO SDK>   Absolute path to AM62xx EVM TI SDK

Options:
  -h, --help   Show this help and exit
EOF
}

check_sdk_install() {
    # Check if specified SDK directory exists, if not return error
    if [ ! -d "${SDK_PATH}" ]; then
        echo "Error: SDK path specified does not exist: $SDK_PATH"
        usage
        exit 1
    fi

    echo "SDK destination: $SDK_PATH"
    
    # Check if Rules.make exists, if not return error
    if [ ! -f "${SDK_PATH}/Rules.make" ]; then
        echo "Error: SDK Rules.make does not exist. Something is wrong with SDK install: ${SDK_PATH}Rules.make"
        usage
        exit 1
    fi

    # Check if u-boot folder exists, if not return error
    if [ ! -d "${SDK_PATH}/board-support/ti-u-boot-2024.04+git/" ]; then
        echo "Error: u-boot directory does not exist. Something is wrong with SDK install"
        usage
        exit 1
    fi

    # Check if kernel folder exists, if not return error
    if [ ! -d "${SDK_PATH}/board-support/ti-linux-kernel-6.6.58+git-ti/" ]; then
        echo "Error: kernel directory does not exist. Something is wrong with SDK install"
        usage
        exit 1
    fi
}

patch_rules() {
    # Override Rules.make for OSD625-PM BRK
    sed -i 's/INSTALL_MOD_STRIP?=1/INSTALL_MOD_STRIP?=0/' ${SDK_PATH}/Rules.make
    sed -i 's/PLATFORM?=am62xx-evm/PLATFORM?=am625-osd625-brk/' ${SDK_PATH}/Rules.make
    sed -i 's/UBOOT_MACHINE=am62x_evm_a53_defconfig/UBOOT_MACHINE=am62x_osd62x_a53_defconfig/' ${SDK_PATH}/Rules.make
    sed -i 's/UBOOT_MACHINE_R5=am62x_evm_r5_defconfig/UBOOT_MACHINE_R5=am62x_osd62x_r5_defconfig/' ${SDK_PATH}/Rules.make
    sed -i 's/MKIMAGE_DTB_FILE=a53\/arch\/arm\/dts\/k3-am625-sk.dtb/MKIMAGE_DTB_FILE=a53\/arch\/arm\/dts\/k3-am625-osd625-brk.dtb/' ${SDK_PATH}/Rules.make
}

patch_uboot() {
    echo "Patching u-boot: ${SDK_PATH}/board-support/ti-u-boot-2024.04+git/"
    cd ${SDK_PATH}/board-support/ti-u-boot-2024.04+git/
    for p in `ls -a ${BRK_PATH}/ti-u-boot-2024.04+git/*patch`;do patch -p1 < $p; done

    # Patching u-boot jailhouse
    cd ${SDK_PATH}/board-support/u-boot-extras-jailhouse-2024.04+git/
    for p in `ls -a ${BRK_PATH}/ti-u-boot-2024.04+git/*patch`;do patch -p1 < $p; done
    cd ${BRK_PATH}
}

patch_kernel() {
    echo "Patching u-boot: ${SDK_PATH}/board-support/ti-linux-kernel-6.6.58+git-ti/"
    cd ${SDK_PATH}/board-support/ti-linux-kernel-6.6.58+git-ti/
    for p in `ls -a ${BRK_PATH}/ti-linux-kernel-6.6.58+git-ti/*patch`;do patch -p1 < $p; done

    # Patching kernel jailhouse
    cd ${SDK_PATH}/board-support/linux-extras-6.6.58+git-ti/
    for p in `ls -a ${BRK_PATH}/ti-linux-kernel-6.6.58+git-ti/*patch`;do patch -p1 < $p; done
    cd ${BRK_PATH}
}

add_brk_prebuilt() {
    # copy prebuilt images to SDK location
    cp -R ${BRK_PATH}/prebuilt-images/am625-osd625-brk  ${SDK_PATH}/board-support/prebuilt-images
    cp -R ${BRK_PATH}/prebuilt-images/am625-osd625-brk  ${SDK_PATH}/board-support/prebuilt-images/am625-osd625-brk-jailhouse
}

reset_sdk() {
    echo "resetting ${SDK_PATH}/board-support/linux-extras-6.6.58+git-ti/"
    cd ${SDK_PATH}/board-support/linux-extras-6.6.58+git-ti/
    git reset --hard 9419c55
    git clean -fdx

    echo "resetting ${SDK_PATH}/board-support/ti-linux-kernel-6.6.58+git-ti/"
    cd ${SDK_PATH}/board-support/ti-linux-kernel-6.6.58+git-ti/
    git reset --hard a7758da
    git clean -fdx
    
    echo "resetting ${SDK_PATH}/board-support/ti-u-boot-2024.04+git/"
    cd ${SDK_PATH}/board-support/ti-u-boot-2024.04+git/
    git reset --hard 29d0c23
    git clean -fdx
    
    echo "resetting ${SDK_PATH}/board-support/u-boot-extras-jailhouse-2024.04+git/"
    cd ${SDK_PATH}/board-support/u-boot-extras-jailhouse-2024.04+git/
    git reset --hard 5d20b4b
    git clean -fdx
    cd ${BRK_PATH}
    echo "SDK: ${SDK_PATH} is reset to original state"
}

# -------- argument parsing --------
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi

if [ "$1" = "-r" ] || [ "$1" = "--reset" ]; then
    if [ $# -ne 2 ]; then
        usage
        exit 0
    fi
    SDK_PATH=$(realpath $2)
    reset_sdk
    exit 0
fi

# Require exactly 1 positional argument
if [ $# -ne 1 ]; then
    echo "Error: Expected 1 arguments, got $#." >&2
    usage
    exit 1
fi

SDK_PATH=$(realpath $1)
BRK_PATH=$(pwd)

echo "Checking SDK"
check_sdk_install
echo "Patching Rules.make"
patch_rules
echo "Patching u-boot"
patch_uboot
echo "Patching Linux kernel"
patch_kernel
echo "Adding pre-built images needed for build"
add_brk_prebuilt

