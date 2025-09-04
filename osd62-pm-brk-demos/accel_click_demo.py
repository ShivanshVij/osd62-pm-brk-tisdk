"""
--------------------------------------------------------------------------
OSD62-PM-BRK - ADXL345 Accelerometer Driver (i2c_tools)
--------------------------------------------------------------------------
License:
Copyright 2025, Octavo Systems, LLC

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------

This script can be used to read X, Y acceleration values from
IIS2DH Accelerometer over I2C bus using i2c_tools.

"""
import os
import time
import subprocess


# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------

# Controller Constants
X_DIR                           = 0
Y_DIR                           = 1
Z_DIR                           = 2


# ADXL345 Constants
ADXL345_I2C_BUS                 = " 1"
ADXL345_IMU_ADDR                = " 0x1d"

ADXL_DEVID                      = 0x00
ADXL345_DATA_FORMAT             = 0x31
ADXL345_BW_RATE                 = 0x2C
ADXL345_POWER_CTL               = 0x2D

# ADXL345 configuration
ADXL_DEVID_VALUE                = 0xE5
ADXL345_BW_RATE_400HZ           = 0x0D
ADXL345_RANGE_2G                = 0x00
ADXL345_RANGE_4G                = 0x01
ADXL345_DATA_FORMAT_16          = 0x08
ADXL345_MEASURE_EN              = 0x08

# Mapping between direction variables and addresses:
DIR_REG_MAP = {
  X_DIR : "0x32",
  Y_DIR : "0x34",
  Z_DIR : "0x36"
}


# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------

# I2C set command:  {0} = bus, {1} = addr, {2} = reg, {3} = value
i2cset_cmd                      = "i2cset -y {0} {1} {2} {3}"

# I2C get command:  {0} = bus, {1} = addr, {2} = reg w - word format(16 bit)
i2cget_cmd_w                      = "i2cget -y {0} {1} {2} w"

# I2C get command:  {0} = bus, {1} = addr, {2} = reg -8 bit
i2cget_cmd_b                      = "i2cget -y {0} {1} {2}"

# ------------------------------------------------------------------------
# Functions / Classes
# ------------------------------------------------------------------------

class IMU():
    """ ADXL345 Driver Class """
    i2c_bus    = None
    i2c_addr   = None
    debug      = None

    def __init__(self, i2c_bus=ADXL345_I2C_BUS, i2c_addr=ADXL345_IMU_ADDR, debug=False):
        """ Initialize variables and call setup function
              - Default MPU Address:  0x1d on I2C1
        """
        self.debug      = debug
        self.i2c_bus    = i2c_bus
        self.i2c_addr   = i2c_addr

        try:
            id_value = int(subprocess.check_output(i2cget_cmd_b.format(self.i2c_bus, self.i2c_addr, ADXL_DEVID), shell = True).strip().decode('ascii'), 0)

        except subprocess.CalledProcessError as e:
            msg = f"Failed to read ADXL DEVID on bus {self.i2c_bus} addr {self.i2c_addr}"
            if e.returncode == 2:
                msg += " (exit status 2: check bus number, device address, wiring, and permissions)."
            if e.stderr:
                msg += f" Stderr: {e.stderr.strip()}"
            raise RuntimeError(msg) from e
        self._setup()

    # End def


    def _setup(self):
        """Setup the ADXL345"""
        # Set Data Rate to 400Hz
        os.system(i2cset_cmd.format(self.i2c_bus, self.i2c_addr, ADXL345_BW_RATE, ADXL345_BW_RATE_400HZ))

        # Set data format to 16 bit
        os.system(i2cset_cmd.format(self.i2c_bus, self.i2c_addr, ADXL345_DATA_FORMAT, ADXL345_DATA_FORMAT_16 | ADXL345_RANGE_2G))

        # Enable measurement
        os.system(i2cset_cmd.format(self.i2c_bus, self.i2c_addr, ADXL345_POWER_CTL, ADXL345_MEASURE_EN))
    # End def


    def _convert(self, val):
        """ Convert IMU output register from:
            two's complement, Right justified format to integer
        """
        if(val & (1 << 16 - 1)):
            val = val - (1<<16)

        return val
        
    # End def
    
    
    def read(self, direction):
        """ Return the IMU value for the provided direction """
        try:
            addr = DIR_REG_MAP[direction]
        except:
            print("ERROR:  Direction {0} not supported.".format(direction))
            return 0

        # Perform measurement
        val = int(subprocess.check_output(i2cget_cmd_w.format(self.i2c_bus, self.i2c_addr, addr), shell = True).strip().decode('ascii'), 0)

        return self._convert(val)
    
    # End def


    def cleanup(self):
        """Cleanup the hardware components."""
        pass            # Nothing to be done for IIS2DH 

    # End def

# End class


# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------

if __name__ == '__main__':
    # Test Driver and profile performance

    print("Read ADXL345 via i2c_tools")

    # Profile setup time    
    start_time = time.time()

    # Instantiate Read Accelerometer Class
    imu = IMU()

    print("Setup time: {0} ms".format(round((time.time() - start_time) * 1000,1)))
    
    # Read and print acceleration values
    #   - User can stop with "Ctrl-C"
    try:
        while True:
            # Sleep time determines the interval between data reads
            time.sleep(1)

            # Read IMU
            start_time = time.time()
            
            x = imu.read(X_DIR)
            y = imu.read(Y_DIR)
            z = imu.read(Z_DIR)
            
            # Print X,Y and Z Acceleration Values
            print("Acceleration: ({0}, {1}, {2})  Time: {3} ms".format(x, y, z, round((time.time() - start_time) * 1000, 1)))

        # End while

    except KeyboardInterrupt:
        # Clean up hardware when exiting
        imu.cleanup()

    print("Reading ADXL345 Complete")
