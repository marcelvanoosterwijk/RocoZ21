# RocoZ21
Python library for interfacing with Roco Z21 DCC Command Station

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
    
This library is implemented as a facad for the Z21 Command Station. The design pattern is Singleton, assuming only one command station is to be used. As such the library is a set of individual functions rather than a class.

The programming style is based on functional programming where possible. This means that all functions are pure, i.e. are stateless and contain no side effects.
Only the final IO functions are non-pure. All functions that interpret incoming messages have correctness checks. This may be unnecessary, assuming that the Z21 will not send any incorrect messages and no errors are made during the handling of incoming messages in this library. Variables are used to keep the functions readable and match the specifications. They only exist within the context of the functions. No global variables are used. Also, the variables once created, are never mutated.

Comments beyond reference of the functions to the specifications are limited to a minumum.
