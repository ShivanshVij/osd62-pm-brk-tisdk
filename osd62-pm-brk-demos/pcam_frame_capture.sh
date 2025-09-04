#!/bin/sh
# This script captures a single frame on OSD62-PM-BRK
# Camera module: https://digilent.com/shop/pcam-5c-5-mp-fixed-focus-color-camera-module/
# Setup:
# The varibale "fdtoverlays" in "microSD" lable /boot/firmware/extlinux/extlinux.conf 
# must have "/overlays/k3-am625-osd625-brk-csi2-ov5640.dtbo" to invoke the camera driver
gst-launch-1.0 \
  v4l2src device=/dev/video0 num-buffers=1 ! \
  "video/x-raw,format=UYVY,width=640,height=480" ! \
  jpegenc ! \
  filesink location=pcam_frame.jpg
