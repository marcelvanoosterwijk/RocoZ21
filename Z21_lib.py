""" Python library for Roco/Fleischmann Z21

    By Marcel van Oosterwijk
    
    Blog: Marcel's Explorations in Automation
    www.marcelvanoosterwijk.com

    version 1.0, 2019-07-28

    Based on "Z21 LAN Protocol Specification" version 1.09 by Roco
    
    Supported functions in this library:

    2. System, status, versions:
    2.1 LAN_GET_SERIAL_NUMBER (send and receive)
    2.2 LAN_LOGOFF (send)
    2.3 LAN_X_GET_VERSION (send and receive)
    2.4 LAN_X_GET_STATUS (send)
    2.5 LAN_X_SET_TRACK_POWER_OFF (send)
    2.6 LAN_X_SET_TRACK_POWER_ON (send)
    2.7 LAN_X_BC_TRACK_POWER_OFF (receive)
    2.8 LAN_X_BC_TRACK_POWER_ON (receive)
    2.9 LAN_X_BC_PROGRAMMING_MODE (receive)
    2.10 LAN_X_BC_TRACK_SHORT_CIRCUIT (receive)
    2.11 LAN_X_UNKNOWN_COMMAND (receive)
    2.12 LAN_X_STATUS_CHANGED (receive)
    2.13 LAN_X_SET_STOP (send)
    2.14 LAN_X_BC_STOPPED (receive)
    2.15 LAN_X_GET_FIRMWARE_VERSION (send and receive)
    2.16 LAN_SET_BROADCASTFLAGS
    2.17 LAN_GET_BROADCASTFLAGS (send and receive)
    2.18 LAN_SYSTEMSTATE_DATACHANGED (receive)
    2.19 LAN_SYSTEMSTATE_GETDATA (send)
    2.20 LAN_GET_HWINFO (send and receive)
    2.21 LAN_GET_CODE (send and receive)

    4. Driving:
    4.1 LAN_X_GET_LOCO_INFO (send)
    4.2 LAN_X_SET_LOCO_DRIVE (send)
    4.3 LAN_X_SET_LOCO_FUNCTION (send)
    4.4 LAN_X_LOCO_INFO (receive)

    5. Switching:
    5.1 LAN_X_GET_TURNOUT_INFO (send)
    5.2 LAN_X_SET_TURNOUT (send)
    5.3 LAN_X_TURNOUT_INFO (receive)

    7. Feedback - R-Bus:
    7.1 LAN_RMBUS_DATACHANGED (receive)
    7.2 LAN_RMBUS_GETDATA (send)

    Out of scope are:
    3. Settings
    6. Reading and writing decoder CVs
    8. Railcom
    9. LocoNet
    10. CAN
    
    This library is implemented as a facad for the Z21 Command Station.
    The design pattern is Singleton, assuming only one command station is to be used.
    As such the library is a set of individual functions rather than a class.
    The programming style is based on functional programming where possible.
    This means that all functions are pure, i.e. are stateless and contain no side effects.
    Only the final IO functions are non-pure.
    All functions that interpret incoming messages, have correctness checks.
    This may be unnecessary, assuming that the Z21 will not send any incorrect messages
    And no errors are made during the handling of incoming messages in this library.
    Variables are used to keep the functions readable and match the specifications.
    They only exist within the context of the functions. No global variables are used.
    Also, the variables once created, are never mutated.
    Comments beyond reference of the functions to the specifications,
    are limited to a minumum.
"""

def bcdNibbles(db):
    highNibble = db >> 4
    lowNibble = db & 0b1111
    return highNibble, lowNibble
    
def sendLanGetSerialNumber(): # 2.1 LAN_GET_SERIAL_NUMBER
    dataLen = 0x0004
    header = 0x0010
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little")

def receiveLanGetSerialNumber(record): # 2.1 LAN_GET_SERIAL_NUMBER
    if len(record) != 0x0008:
        return
    dataLen = int.from_bytes(record[0:2], byteorder = "little")
    header = int.from_bytes(record[2:4], byteorder = "little")
    correctRecord = \
        dataLen == 0x0008 and \
        header == 0x0010
    data = record[4:]
    serialNumber = int.from_bytes(data, byteorder = "little")
    return \
        { "Message": "LAN_GET_SERIAL_NUMBER",
          "Serial Number": serialNumber } if correctRecord else \
        { "record error" }

def sendLanLogoff(): # 2.2 LAN_LOGOFF
    dataLen = 0x0004
    header = 0x0030
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little")

def sendLanXGetVersion(): # 2.3 LAN_X_GET_VERSION
    dataLen = 0x0007
    header = 0x0040
    xHeader = 0x21
    db0 = 0x21
    xor = 0x00 # xHeader ^ db0
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little") + \
        int.to_bytes(xHeader, 1, byteorder = "little") + \
        int.to_bytes(db0, 1, byteorder = "little") + \
        int.to_bytes(xor, 1, byteorder = "little")

def receiveLanXGetVersion(record): # 2.3 LAN_X_GET_VERSION
    if len(record) != 0x0009:
        return
    dataLen = int.from_bytes(record[0:2], byteorder = "little")
    header = int.from_bytes(record[2:4], byteorder = "little")
    data = record[4:]
    xHeader = data[0]
    db0 = data[1]
    db1 = data[2]
    db2 = data[3]
    xor = data[4]
    correctRecord = \
        dataLen == 0x0009 and \
        header == 0x0040 and \
        xHeader == 0x63 and \
        db0 == 0x21 and \
        xor == xHeader ^ db0 ^ db1 ^ db2
    # BCD format: 0x36 --> version 3.6
    majVersion, minVersion = bcdNibbles(db1)
    commandStationId = \
        "Z21" if db2 == 0x12 else \
        "z21" if db2 == 0x13 else \
        "unknown"
    return \
        { "Message": "LAN_X_GET_VERSION",
          "X-Bus major version": majVersion,
          "X-Bus minor version": minVersion,
          "Command station ID": commandStationId } if correctRecord else \
        { "record error" }

def sendLanXGetStatus(): # 2.4 LAN_X_GET_STATUS
    dataLen = 0x0007
    header = 0x0040
    xHeader = 0x21
    db0 = 0x24
    xor = 0x05  # xHeader ^ db0
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little") + \
        int.to_bytes(xHeader, 1, byteorder = "little") + \
        int.to_bytes(db0, 1, byteorder = "little") + \
        int.to_bytes(xor, 1, byteorder = "little")

def sendLanXSetTrackPowerOff(): # 2.5 LAN_X_SET_TRACK_POWER_OFF
    dataLen = 0x0007
    header = 0x0040
    xHeader = 0x21
    db0 = 0x80
    xor = 0xA1 # xHeader ^ db0
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little") + \
        int.to_bytes(xHeader, 1, byteorder = "little") + \
        int.to_bytes(db0, 1, byteorder = "little") + \
        int.to_bytes(xor, 1, byteorder = "little")

def sendLanXSetTrackPowerOn(): # 2.6 LAN_X_SET_TRACK_POWER_ON
    dataLen = 0x0007
    header = 0x0040
    xHeader = 0x21
    db0 = 0x81
    xor = 0xA0 # xHeader ^ db0
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little") + \
        int.to_bytes(xHeader, 1, byteorder = "little") + \
        int.to_bytes(db0, 1, byteorder = "little") + \
        int.to_bytes(xor, 1, byteorder = "little")

def receiveLanXBc(record):  # 2.7 LAN_X_BC_TRACK_POWER_OFF
                            # 2.8 LAN_X_BC_TRACK_POWER_ON
                            # 2.9 LAN_X_BC_PROGRAMMING_MODE
                            # 2.10 LAN_X_BC_TRACK_SHORT_CIRCUIT
                            # 2.11 LAN_X_UNKNOWN_COMMAND
    if len(record) != 0x0007:
        return
    dataLen = int.from_bytes(record[0:2], byteorder = "little")
    header = int.from_bytes(record[2:4], byteorder = "little")
    data = record[4:]
    xHeader = data[0]
    db0 = data[1]
    xor = data[2]
    correctRecord = \
        dataLen == 0x0007 and \
        header == 0x0040 and \
        xHeader == 0x61 and \
        xor == xHeader ^ db0
    message = \
        "LAN_X_BC_TRACK_POWER_OFF" if db0 == 0x00 else \
        "LAN_X_BC_TRACK_POWER_ON" if db0 == 0x01 else \
        "LAN_X_BC_PROGRAMMING_MODE" if db0 == 0x02 else \
        "LAN_X_BC_TRACK_SHORT_CIRCUIT" if db0 == 0x08 else \
        "LAN_X_UNKNOWN_COMMAND" if db == 0x82 else \
        "unknown"
    return  \
        { "Message": message } if correctRecord else \
        { "record error" }

def receiveLanXStatusChanged(record): # 2.12 LAN_X_STATUS_CHANGED
    if len(record) != 0x0008:
        return
    dataLen = int.from_bytes(record[0:2], byteorder = "little")
    header = int.from_bytes(record[2:4], byteorder = "little")
    data = record[4:]
    xHeader = data[0]
    db0 = data[1]
    db1 = data[2]
    xor = data[3]
    correctRecord = \
        dataLen == 0x0008 and \
        header == 0x0040 and \
        xHeader == 0x62 and \
        db0 == 0x22 and \
        xor == xHeader ^ db0 ^ db1
    status = \
        "Emergency Stop" if db1 & 0x01 else \
        "Track Voltage Off" if db1 & 0x02 else \
        "Short Circuit" if db1 & 0x04 else \
        "Programming Mode Active" if db1 & 0x20 else \
        "unknown"
    return \
        { "Message": "LAN_X_STATUS_CHANGED",
          "Status": status } if correctRecord else \
        { "record error" }

def sendLanXSetStop(): # 2.13 LAN_X_SET_STOP
    dataLen = 0x0006
    header = 0x0040
    xHeader = 0x80
    xor = 0x80 # xHeader ^ db0
    return \
        int.to_bytes(dataLen, 2, byteorder = 'little') + \
        int.to_bytes(header, 2, byteorder = 'little') + \
        int.to_bytes(xHeader, 1, byteorder = 'little') + \
        int.to_bytes(xor, 1, byteorder = 'little')

def receiveLanXBcStopped(record): # 2.14 LAN_X_BC_STOPPED
    if len(record) != 0x0007:
        return
    dataLen = int.from_bytes(record[0:2], byteorder = "little")
    header = int.from_bytes(record[2:4], byteorder = "little")
    data = record[4:]
    xHeader = int.from_bytes(data[0:1], byteorder = "little")
    db0 = int.from_bytes(data[1:2], byteorder = "little")
    xor = int.from_bytes(data[2:3], byteorder = "little")
    correctRecord = \
        dataLen == 0x0007 and \
        header == 0x0040 and \
        xHeader == 0x81 and \
        db0 == 0x00 and \
        xor == 0x81 # xHeader ^ db0
    return \
        { "Message": "LAN_X_BC_STOPPED" } if correctRecord else \
        { "record error" }

def sendLanXGetFirmwareVersion(): # 2.15 LAN_X_GET_FIRMWARE_VERSION
    dataLen = 0x0007
    header = 0x0040
    xHeader = 0xF1
    db0 = 0x0A
    xor = 0xFB  # xHeader ^ db0
    return \
        int.to_bytes(dataLen, 2, byteorder = 'little') + \
        int.to_bytes(header, 2, byteorder = 'little') + \
        int.to_bytes(xHeader, 1, byteorder = 'little') + \
        int.to_bytes(db0, 1, byteorder = 'little') + \
        int.to_bytes(xor, 1, byteorder = 'little')

def receiveLanXGetFirmwareVersion(record): # 2.15 LAN_X_GET_FIRMWARE_VERSION
    if len(record) != 0x0009:
        return
    dataLen = int.from_bytes(record[0:2], byteorder = "little")
    header = int.from_bytes(record[2:4], byteorder = "little")
    data = record[4:]
    xHeader = data[0]
    db0 = data[1]
    db1 = data[2]
    db2 = data[3]
    xor = data[4]
    correctRecord = \
        dataLen == 0x0009 and \
        header == 0x0040 and \
        xHeader == 0xF3 and \
        db0 == 0x0A and \
        xor == xHeader ^ db0 ^ db1 ^ db2
    db1H, db1L = bcdNibbles(db1)
    db2H, db2L = bcdNibbles(db2)
    majVersion = 10 * db1H + db1L
    minVersion = 10 * db2H + db2L
    return \
        { "Message": "LAN_X_GET_FIRMWARE_VERSION",
          "Major version": majVersion,
          "Minor version": minVersion } if correctRecord else \
        { "record error" }

def sendLanSetBroadcastflags(): # 2.16 LAN_SET_BROADCASTFLAGS
    # Note: this function subscribes to all messages suitable for automated driving.
    # Hence the data bytes are fixed rather than based on input parameters.
    dataLen = 0x0008
    header = 0x0050
    data = 0x00010101
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little") + \
        int.to_bytes(data, 4, byteorder = "little")

def sendLanGetBroadcastflags(): # 2.17 LAN_GET_BROADCASTFLAGS
    dataLen = 0x0004
    header = 0x0051
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little")

def receiveLanGetBroadcastflags(record): # 2.17 LAN_GET_BROADCASTFLAGS
    if len(record) != 0x0008:
        return
    dataLen = int.from_bytes(record[0:2], byteorder = "little")
    header = int.from_bytes(record[2:4], byteorder = "little")
    correctRecord = \
        dataLen == 0x0008 and \
        header == 0x0051
    data = record[4:]
    broadcastFlags = int.from_bytes(data, byteorder = "little")
    return \
        { "Message": "LAN_GET_BROADCASTFLAGS",
          "Broadcast Flags": broadcastFlags } if correctRecord else \
        { "record error" }

def receiveLanSystemstateDatachanged(record): # 2.18 LAN_SYSTEMSTATE_DATACHANGED
    if len(record) != 0x0014:
        return
    dataLen = int.from_bytes(record[0:2], byteorder = "little")
    header = int.from_bytes(record[2:4], byteorder = "little")
    correctRecord = \
        dataLen == 0x0014 and \
        header == 0x0084
    data = record[4:]

    mainCurrent = int.from_bytes(data[0:2], byteorder = "little")
    progCurrent = int.from_bytes(data[2:4], byteorder = "little")
    filteredMainCurrent = int.from_bytes(data[4:6], byteorder = "little")
    temp = int.from_bytes(data[6:8], byteorder = "little")
    supplyVoltage = int.from_bytes(data[8:10], byteorder = "little")
    vccVoltage = int.from_bytes(data[10:12], byteorder = "little")

    csEmergencyStop = (data[12] & 0x01)
    csTrackVoltageOff = (data[12] & 0x02)
    csShortCircuit = (data[12] & 0x04)
    csProgrammingModeActive = (data[12] & 0x20)
    
    cseHighTemperature = (data[13] & 0x01)
    csePowerLost = (data[13] & 0x02)
    cseShortCircuitExternal = (data[13] & 0x04)
    cseShortCircuitInternal = (data[13] & 0x08)
    return \
        { "Message": "LAN_SYSTEMSTATE_DATACHANGED",
          "mainCurrent": mainCurrent,
          "progCurrent": progCurrent,
          "temp": temp,
          "supplyVoltage": supplyVoltage,
          "vccVoltage": vccVoltage,
          "csEmergencyStop": csEmergencyStop,
          "csTrackVoltageOff": csTrackVoltageOff,
          "csShortCircuit": csShortCircuit,
          "csProgrammingModeActive": csProgrammingModeActive,
          "cseHighTemperature": cseHighTemperature,
          "csePowerLost": csePowerLost,
          "cseShortCircuitExternal": cseShortCircuitExternal,
          "cseShortCircuitInternal": cseShortCircuitInternal } if correctRecord else \
        { "record error" }

def sendLanSystemstateGetdata(): # 2.19 LAN_SYSTEMSTATE_GETDATA
    dataLen = 0x0004
    header = 0x0085
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little")

def sendLanGetHwInfo(): # 2.20 LAN_GET_HWINFO
    dataLen = 0x0004
    header = 0x001A
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little")

def receiveLanGetHwInfo(record): # 2.20 LAN_GET_HWINFO
    if len(record) != 0x000C:
        return
    dataLen = int.from_bytes(record[0:2], byteorder = "little")
    header = int.from_bytes(record[2:4], byteorder = "little")
    correctRecord = \
        dataLen == 0x000C and \
        header == 0x001A
    data = record[4:]
    hwCode = int.from_bytes(data[0:4], byteorder = "little")
    hwType = \
        "D_HWT_Z21_OLD" if hwCode == 0x00000200 else \
        "D_HWT_Z21_NEW" if hwCode == 0x00000201 else \
        "D_HWT_Z21_SMARTRAIL" if hwCode == 0x00000202 else \
        "D_HWT_z21_SMALL" if hwCode == 0x00000203 else \
        "D_HWT_z21_START" if hwCode == 0x00000204 else \
        "unknown"
    db4H, db4L = bcdNibbles(data[4])
    db5H, db5L = bcdNibbles(data[5])
    minVersion = 10 * db4H + db4L
    majVersion = 10 * db5H + db5L
    return \
        { "Message": "LAN_GET_HWINFO",
          "Hardware Type": hwType,
          "Firmware Major Version": majVersion,
          "Firmware Minor Version": minVersion } if correctRecord else \
        { "record error" }

def sendLanGetCode(): # 2.21 LAN_GET_CODE
    dataLen = 0x0004
    header = 0x0018
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little")

def receiveLanGetCode(record): # 2.21 LAN_GET_CODE
    if len(record) != 0x0005:
        return
    dataLen = int.from_bytes(record[0:2], byteorder = "little")
    header = int.from_bytes(record[2:4], byteorder = "little")
    correctRecord = \
        dataLen == 0x0005 and \
        header == 0x0018
    data = record[4:]
    swCode = int.from_bytes(data[0:4], byteorder = "little")
    swType = \
        "Z21_NO_LOCK" if swCode == 0x00 else \
        "Z21_START_LOCKED" if swCode == 0x01 else \
        "Z21_START_UNLOCKED" if swCode == 0x02 else \
        "unknown"
    return \
        { "Message": "LAN_GET_HWINFO",
          "Software Feature Scope": swType } if correctRecord else \
        { "record error" }

def sendLanXGetLocoInfo(address): # 4.1 LAN_X_GET_LOCO_INFO
    dataLen = 0x0009
    header = 0x0040
    xHeader = 0xE3
    db0 = 0xF0
    db1 = 0
    db2 = address
    xor = xHeader ^ db0 ^ db1 ^ db2
    return  \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little") + \
        int.to_bytes(xHeader, 1, byteorder = "little") + \
        int.to_bytes(db0, 1, byteorder = "little") + \
        int.to_bytes(db1, 1, byteorder = "little") + \
        int.to_bytes(db2, 1, byteorder = "little") + \
        int.to_bytes(xor, 1, byteorder = "little")

def sendLanXSetLocoDrive(address, direction, speed, stop): # 4.2 LAN_X_SET_LOCO_DRIVE
    # Note: this function will always use 128 speed steps.
    # direction: 'forward' or 'backward'
    # speed: 0 - 126
    # stop: 'none', 'normal', 'emergency'
    dataLen = 0x000A
    header = 0x0040
    xHeader = 0xE4
    db0 = 0x13
    db1 = 0
    db2 = address
    codingSpeed = \
        0 if stop == "normal" or speed == 0 else \
        1 if stop == "emergency" else \
        speed + 1
    db3 = \
        codingSpeed | 0b10000000 if direction == "forward" else \
        codingSpeed & ~0b10000000
    xor = xHeader ^ db0 ^ db1 ^ db2 ^ db3
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little") + \
        int.to_bytes(xHeader, 1, byteorder = "little") + \
        int.to_bytes(db0, 1, byteorder = "little") + \
        int.to_bytes(db1, 1, byteorder = "little") + \
        int.to_bytes(db2, 1, byteorder = "little") + \
        int.to_bytes(db3, 1, byteorder = "little") + \
        int.to_bytes(xor, 1, byteorder = "little")

def sendLanXSetLocoFunction(address, function, switchMode): # 4.3 LAN_X_SET_LOCO_FUNCTION
    # function: decimal, 1 - 63 (should not be more than 28)
    # switchMode: 'on', 'off' or 'switch'
    dataLen = 0x000A
    header = 0x0040
    xHeader = 0xE4
    db0 = 0xF8
    db1 = 0
    db2 = address
    db3 = \
        function & ~0b11000000 if switchMode == "off" else \
        function & ~0b10000000 | 0b01000000 if switchMode == "on" else \
        function | 0b10000000 & ~0b01000000
    xor = xHeader ^ db0 ^ db1 ^ db2 ^ db3
    return  \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little") + \
        int.to_bytes(xHeader, 1, byteorder = "little") + \
        int.to_bytes(db0, 1, byteorder = "little") + \
        int.to_bytes(db1, 1, byteorder = "little") + \
        int.to_bytes(db2, 1, byteorder = "little") + \
        int.to_bytes(db3, 1, byteorder = "little") + \
        int.to_bytes(xor, 1, byteorder = "little")

def receiveLanXLocoInfo(record): # 4.4 LAN_X_LOCO_INFO
    if len(record) < 14 or len(record) > 21: # NOT ready for future DB8 - DB14!
        return
    dataLen = int.from_bytes(record[0:2], byteorder = "little")
    header = int.from_bytes(record[2:4], byteorder = "little")
    data = record[4:]
    xHeader = data[0]
    xor = data[4]
    correctRecord = \
        dataLen >= 14 and dataLen >= 21 and \
        header == 0x0040 and \
        xHeader == 0xEF
    locInfo = record[5:]
    address = int.from_bytes(locInfo[0:2], byteorder = "big")
    busy = locInfo[2] & 0b00001000 != 0
    res = \
        14 if locInfo[2] & 0b00000111 == 0 else \
        18 if locInfo[2] & 0b00000111 == 2 else \
        128
    direction = \
        "forward" if locInfo[3] & 0b10000000 != 0 else \
        "backward"
    speed = locInfo[3] & 0b01111111
    doubletraction = locInfo[4] & 0b01000000 != 0
    smartsearch = locInfo[4] & 0b00100000 != 0
    f = [
        locInfo[4] & 0b00010000 != 0, # f[0] = light
        locInfo[4] & 0b00000001 != 0,
        locInfo[4] & 0b00000010 != 0,
        locInfo[4] & 0b00000100 != 0,
        locInfo[4] & 0b00001000 != 0,
        locInfo[5] & 0b00000001 != 0,
        locInfo[5] & 0b00000010 != 0,
        locInfo[5] & 0b00000100 != 0,
        locInfo[5] & 0b00001000 != 0,
        locInfo[5] & 0b00010000 != 0,
        locInfo[5] & 0b00100000 != 0,
        locInfo[5] & 0b01000000 != 0,
        locInfo[5] & 0b10000000 != 0,
        locInfo[6] & 0b00000001 != 0,
        locInfo[6] & 0b00000010 != 0,
        locInfo[6] & 0b00000100 != 0,
        locInfo[6] & 0b00001000 != 0,
        locInfo[6] & 0b00010000 != 0,
        locInfo[6] & 0b00100000 != 0,
        locInfo[6] & 0b01000000 != 0,
        locInfo[6] & 0b10000000 != 0,
        locInfo[7] & 0b00000001 != 0,
        locInfo[7] & 0b00000010 != 0,
        locInfo[7] & 0b00000100 != 0,
        locInfo[7] & 0b00001000 != 0,
        locInfo[7] & 0b00010000 != 0,
        locInfo[7] & 0b00100000 != 0,
        locInfo[7] & 0b01000000 != 0,
        locInfo[7] & 0b10000000 != 0 #f[28]
        ]
    return \
        { "Message": "LAN_X_LOCO_INFO",
          "address": address,
          "busy": busy,
          "res": res,
          "direction": direction,
          "speed": speed,
          "doubletraction": doubletraction,
          "smartsearch": smartsearch,
          "functions": f } if correctRecord else \
        { "record error" }

def sendLanXGetTurnoutInfo(address): # 5.1 LAN_X_GET_TURNOUT_INFO
    if address < 1 or address > 255:
        return
    dataLen = 0x0008
    header = 0x0040
    xHeader = 0x43
    db0 = 0
    db1 = address - 1
    xor = xHeader ^ db0 ^ db1
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little") + \
        int.to_bytes(xHeader, 1, byteorder = "little") + \
        int.to_bytes(db0, 1, byteorder = "little") + \
        int.to_bytes(db1, 1, byteorder = "little") + \
        int.to_bytes(xor, 1, byteorder = "little")

def sendLanXSetTurnout(address, pos): # 5.2 LAN_X_SET_TURNOUT
    if address < 1 or address > 255:
        return
    if pos != "straight" and pos != "branched":
        return
    dataLen = 0x0009
    header = 0x0040
    xHeader = 0x53
    db0 = 0
    db1 = address - 1
    # db2: 10Q0A00P where Q = 1, A = 1, P = 0 (branched) or 1 (straight)
    db2 = 0b10101000 if pos == "branched" else 0b10101001
    xor = xHeader ^ db0 ^ db1 ^ db2
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little") + \
        int.to_bytes(xHeader, 1, byteorder = "little") + \
        int.to_bytes(db0, 1, byteorder = "little") + \
        int.to_bytes(db1, 1, byteorder = "little") + \
        int.to_bytes(db2, 1, byteorder = "little") + \
        int.to_bytes(xor, 1, byteorder = "little")

def receiveLanXTurnoutInfo(record): # 5.3 LAN_X_TURNOUT_INFO
    if len(record) != 0x0009:
        return
    dataLen = int.from_bytes(record[0:2], byteorder = "little")
    header = int.from_bytes(record[2:4], byteorder = "little")
    data = record[4:]
    xHeader = data[0]
    db0 = data[1]
    db1 = data[2]
    db2 = data[3]
    xor = data[4]
    correctRecord = \
        dataLen == 0x0009 and \
        header == 0x0040 and \
        xHeader == 0x43 and \
        xor == xHeader ^ db0 ^ db1 ^ db2
    db = record[5:]
    address = int.from_bytes(db[0:2], byteorder = "big") + 1
    status = \
        "not set" if db[2] == 0 else \
        "branched" if db[2] == 1 else \
        "straight" if db[2] == 2 else \
        "error"
    return \
        { "address": address,
          "status": status } if correctRecord else \
        { "record error" }

def receiveLanRmbusDatachanged(record): # 7.1 LAN_RMBUS_DATACHANGED
    if len(record) != 0x000F:
        return
    dataLen = int.from_bytes(record[0:2], byteorder = "little")
    header = int.from_bytes(record[2:2], byteorder = "little")
    correctRecord = \
        dataLen == 0x000F and \
        header == 0x0080
    data = record[4:]
    groupIndex = data[0]
    feedbackStatus = data[1:]
    
    # Implemented for feedback modules 1 and 2
    fm1 = [
        feedbackStatus[0] & 0b00000001, # channel 1
        feedbackStatus[0] & 0b00000010,
        feedbackStatus[0] & 0b00000100,
        feedbackStatus[0] & 0b00001000,
        feedbackStatus[0] & 0b00010000,
        feedbackStatus[0] & 0b00100000,
        feedbackStatus[0] & 0b01000000,
        feedbackStatus[0] & 0b10000000 # channel 8
    ]
    fm2 = [
        feedbackStatus[1] & 0b00000001,
        feedbackStatus[1] & 0b00000010,
        feedbackStatus[1] & 0b00000100,
        feedbackStatus[1] & 0b00001000,
        feedbackStatus[1] & 0b00010000,
        feedbackStatus[1] & 0b00100000,
        feedbackStatus[1] & 0b01000000,
        feedbackStatus[1] & 0b10000000
    ]
    # This pattern can be extended to feedback module 10
    
    return \
        { "groupIndex": groupIndex,
          "module 1": fm1,
          "module 2": fm2 } if correctRecord else \
        { "record error" }

def sendLanRmbusGetdata(groupIndex): # 7.2 LAN_RMBUS_GETDATA
    if groupIndex < 1 or groupIndex > 2:
        return
    dataLen = 0x0005
    header = 0x0081
    return \
        int.to_bytes(dataLen, 2, byteorder = "little") + \
        int.to_bytes(header, 2, byteorder = "little") + \
        int.to_bytes(groupIndex, 1, byteorder = "little")

def extractRecords(packet):
    return \
        [ ] if len(packet) == 0 else \
        [ "extractRecords error" ] if len(packet) < packet[0] else \
        [ packet[0:packet[0] ] ] + extractRecords(packet[packet[0]:])

def dispatchLanX(record):
    dispatchTable = {
        0x43: receiveLanXTurnoutInfo,
        0x61: receiveLanXBc,
        0x62: receiveLanXStatusChanged,
	0x63: receiveLanXGetVersion,
        0x81: receiveLanXBcStopped,
        0xEF: receiveLanXLocoInfo,
        0xF3: receiveLanXGetFirmwareVersion
    }
    header = int.from_bytes(record[4:5], byteorder = "little")
    return \
	"" if len(record) == 0 else \
	dispatchTable[header](record) if header in dispatchTable else \
	"dispatchLanX error"

def dispatch(record):
    dispatchTable = {
	0x0010: receiveLanGetSerialNumber,
        0x0018: receiveLanGetCode,
        0x001A: receiveLanGetHwInfo,
        0x0040: dispatchLanX,
        0x0051: receiveLanGetBroadcastflags,
        0x0080: receiveLanRmbusDatachanged,
        0x0084: receiveLanSystemstateDatachanged
    }
    header = int.from_bytes(record[2:4], byteorder = "little")
    return \
	"" if len(record) == 0 else \
	dispatchTable[header](record) if header in dispatchTable else \
	"dispatch error"
	
def multiDispatch(recordArray):
    return [dispatch(record) for record in recordArray]

Z21 = ('192.168.0.111', 21105)

# How to use library:

# prerequisites:
# import socket
# import this library

# connect to command station:
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP

# send a command:
# s.sendto(sendLanSetBroadcastflags(), Z21)

# receive records:
# packet, sender = s.recvfrom(1024)
# print(multiDispatch(extractRecords(packet)) if sender == Z21 else "unknown sender")

# disconnect:
# s.close();

