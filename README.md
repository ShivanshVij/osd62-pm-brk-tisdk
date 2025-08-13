[![Static-badge-brk]][OSD62-PM-BRK webpage]
[![Static-badge-pm]][OSD62-PM webpage]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/octavosystems/osd62-pm-brk-tisdk">
    <img src="images/Figure 2 OSD62-PM-BRK Features.png" alt="Logo" width="540" height="286">
  </a>

  <h3 align="center">TI SDK support for OSD62-PM-BRK</h3>

  <p align="center">
    OSD62-PM Breakout Development board
    <a href="https://octavosystems.com/octavo_products/osd62-pm-brk/"><strong>Buy OSD62-PM-BRK</strong></a>
  </p>
</div>

## Requirements
Tested on Ubuntu 22.04 LTS

## Hardware accessories
| Accessory | Webpage |
| ------- | ------- |
| USB to UART adapter | [Buy from Amazon](https://www.amazon.com/HiLetgo-CP2102-Converter-Adapter-Downloader/dp/B00LODGRV8/) |
| Microtips Technology USA (13-101HIEB0HF0-S) 10.1” WUXGA (1920x1200) TFT LCD panel| [Buy from ti.com](https://www.ti.com/tool/SK-LCD1)|
|20624: Type A 40 pin 0.5mm pitch FPC cable for LCD panel| [Buy from Amazon](https://www.amazon.com/uxcell-Flexible-Ribbon-Player-Laptop/dp/B00W8WAICI/) |
|410-358: Digilent Pcam 5C with OV5640 5MP camera|[Buy from digikey.com](https://www.digikey.com/en/products/detail/digilent-inc/410-358/8111762)|
|20624: Type B 15 pin 1mm pitch FPC cable for camera module| [Buy from Amazon](https://www.amazon.com/dp/B0F1N7K82K/ref=sspa_dk_detail_2?th=1) |

## Package versions
| Package | Version | 
| ------- | ------- | 
| TI SDK version | 10.10.10.04 |
| TF-A | v2.11.0 |
| U-Boot | 2024.04 | 
| Linux Kernel | v6.6.58-ti | 

## Wiki page for modifying Beagleboard.org image
Please see https://github.com/octavosystems/osd62-pm-brk-tisdk/wiki/Modifying-a-Beagleboard.org-image-for-OSD62%E2%80%90PM%E2%80%90BRK for procedure to create a Beagleboard.org image for OSD62-PM-BRK

# TI SDK Image for OSD62-PM-BRK
## Preparing an SD card
1. Download TI AM625-SK image from this link: https://dr-download.ti.com/software-development/software-development-kit-sdk/MD-PvdSyIiioq/10.01.10.04/tisdk-default-image-am62xx-evm-10.01.10.04.rootfs.wic.xz
2. Uncompress the file:
   ```
   unxz tisdk-default-image-am62xx-evm-10.01.10.04.rootfs.wic.xz
   ```
3. Conect SD card to Host computer
4. Determine the name of SD card:
   ```
   lsblk
   ```
5. Flash the image to the SD card (Repalce sdX with appropriate path for your SD card):
   ```
   sudo dd if=tisdk-default-image-am62xx-evm-10.01.10.04.rootfs.wic of=/dev/<sdX> bs=10M conv=fdatasync status=progress
   ```
The SD card is now prepared with a default TI AM625-SK image. You will need to modify this SD card to boot OSD62-PM-BRK using the following steps.

## Generating images for OSD62-PM-BRK:
1. Install TI Processor SDK from this link: https://dr-download.ti.com/software-development/software-development-kit-sdk/MD-PvdSyIiioq/10.01.10.04/ti-processor-sdk-linux-am62xx-evm-10.01.10.04-Linux-x86-Install.bin

2. Run TI SDK installation:
   ```
   ./ti-processor-sdk-linux-am62xx-evm-10.01.10.04-Linux-x86-Install.bin
   ```

4. Follow instructions on screen. Choose Destination location: SDK_PATH
5. Run setup.sh to install dependencies and setup SDK - follow prompts
   ```
   cd <PATH TO SDK>
   ./setup.sh
   ```
6. Clone this repository:
   ```
   git clone https://github.com/octavosystems/osd62-pm-brk-tisdk
   ```
7. Change directory to this repository location
   ```
   cd osd62-pm-brk-tisdk/
   ```
8. Make osd625_brk_sdk_setup script executable
   ```
   chmod +x osd625_brk_sdk_setup.sh
   ```
9. Run the setup script from osd62-pm-brk-tisdk(BRK_PATH) location
   ```
   ./osd625_brk_sdk_setup <PATH TO SDK>
   ```
10. Cahnge directory to SDK_PATH
   ```
   cd <PATH TO SDK>
   ```
11. Build u-boot
   ```
   make u-boot
   ```
12. Mount SD card's boot partition (If not automatically mounted. Note that in general, both boot and root partitions automatically mount after you insert the SD card into the Host computer)
   ```
   sudo mount /dev/<sdX>1 /media/<user_name>/boot/
   ```
13. Install u-boot binaries:
    ```
    make u-boot_install DESTDIR=/media/<user_name>/boot/
    ```
14. Install Spalshscreen
    ```
    cp octavo_884x266_32bpp.bmp.gz /media/<user_name>/boot/
    ```
15. Build Linux device trees
    ```
    make linux-dtbs
    ```
16. Mount SD card's root partition (If not automatically mounted. Note that in general, both boot and root partitions automatically mount after you insert the SD card into the Host computer)
    ```
    sudo mount /dev/<sdX>2 /media/<user_name>/root/
    ```
17. Install OSD62-PM-BRK board device tree
    ```
    sudo cp board-support/ti-linux-kernel-6.1.83+gitAUTOINC+c1c2f1971f-ti/arch/arm64/boot/dts/ti/k3-am625-osd625-brk.dtb /media/<user_name>/root/boot/dtb/ti/
    ```
18. Build Linux kernel and kernel modules
    ```
    make linux
    ```
19. Install Linux kernel and kernel modules *Requires 'sudo'
    ```
    sudo make linux_install DESTDIR=/media/<user_name>/root/
    ```
20. [#Optional] Install Display panel device tree overlay
    ```
    sudo cp board-support/ti-linux-kernel-6.1.83+gitAUTOINC+c1c2f1971f-ti/arch/arm64/boot/dts/ti/k3-am625-osd625-brk-microtips-mf101hie-panel.dtbo /media/<user_name>/root/boot/dtb/
    ```
21. [#Optional] Install CSI Camera overlay
    ```
    sudo cp board-support/ti-linux-kernel-6.1.83+gitAUTOINC+c1c2f1971f-ti/arch/arm64/boot/dts/ti/k3-am625-osd625-brk-csi2-ov5640.dtbo /media/<user_name>/root/boot/dtb/
    ```
22. [#optional] Enable Display+Camera overlay. If you only have a display or camera connected, you can remove the other overlay from the command below:
    ```
    echo "name_overlays=k3-am625-osd625-brk-microtips-mf101hie-panel.dtbo k3-am625-osd625-brk-csi2-ov5640.dtbo" >> /media/<user_name>/boot/uEnv.txt
    ```
23. Unmount the SD card
    ```
    sudo umount /media/<user_name>/*
    ```
The SD card is now ready. You can insert the SD card into OSD62-PM-BRK's SD card slot.

## Powering your OSD62-PM-BRK board
1. Connect USB to UART adapter to Host machine USB port
2. Connect UART side of the USB to UART adapter to UART header(JP1) of OSD62-PM-BRK
3. Connect accessories: Camera/Display. Note that the display comes with it's own power supply. Display needs to be powered separately from the board
4. Bring-up a terminal application(Putty/Minicom/picocom) on host machine for the USB to UART adapter:
   ```
   picocom -b 115200 /dev/ttyUSB[x]
   ```
5. Use a USB-C cable to connect the host machine to OSD62-PM-BRK
6. Bootlogs should appeat on the terminal application
7. Board login username: "root". No password is set for this user.
8. Start your application development!

For technical support, please visit: https://octavosystems.com/forums/

<!-- MARKDOWN LINKS & IMAGES -->
[OSD62-PM-BRK webpage]: https://octavosystems.com/octavo_products/osd62-pm-brk/
[OSD62-PM webpage]: https://octavosystems.com/octavo_products/osd62x-pm/
[Static-badge-brk]: https://img.shields.io/badge/OSD62--PM--BRK-FF0000
[Static-badge-pm]: https://img.shields.io/badge/OSD62--PM-FF0000
