"""Virtual Controller Object for Python

Python Implepentation of vXbox from:
http://vjoystick.sourceforge.net/site/index.php/vxbox"""
from ctypes import *
import time
import os
import platform

if platform.architecture()[0] == '32bit':
    arc = '86'
else:
    arc = '64'

_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    'vXboxInterface-x{}'.format(arc),
    'vXboxInterface.dll'
))
_xinput = WinDLL(_path)


class MaxInputsReachedError(Exception):
    """Exception when no inputs are available.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class vController(object):
    """Virtual Controller Object"""
    DPAD_OFF = 0
    DPAD_UP = 1
    DPAD_DOWN = 2
    DPAD_LEFT = 4
    DPAD_RIGHT = 8

    def __init__(self):
        self.id = 0
        self.PlugIn()

    def __del__(self):
        """Unplug self if object is cleaned up"""
        self.UnPlug()

    @property
    def _available_ids(self):
        ids = [x for x in range(
            1, 5) if _xinput.isControllerExists(c_int(x)) == 0]
        if len(ids) == 0:
            raise MaxInputsReachedError('Max Inputs Reached')

        return ids

    def PlugIn(self):
        """Take next available controller id and plug in to Virtual USB Bus"""
        ids = self._available_ids
        self.id = ids[0]

        _xinput.PlugIn(self.id)
        time.sleep(0.5)

    def UnPlug(self, force=False):
        """Unplug controller from Virtual USB Bus and free up ID"""
        if force:
            _xinput.UnPlugForce(c_uint(self.id))
        else:
            _xinput.UnPlug(c_uint(self.id))

    def set_value(self, control, value=None):
        """Set a value on the controller
    All controls will accept a value between -1.0 and 1.0

    Control List:
        AxisLx          , Left Stick X-Axis
        AxisLy          , Left Stick Y-Axis
        AxisRx          , Right Stick X-Axis
        AxisRy          , Right Stick Y-Axis
        BtnBack         , Menu/Back Button
        BtnStart        , Start Button
        BtnA            , A Button
        BtnB            , B Button
        BtnX            , X Button
        BtnY            , Y Button
        BtnThumbL       , Left Thumbstick Click
        BtnThumbR       , Right Thumbstick Click
        BtnShoulderL    , Left Shoulder Button
        BtnShoulderR    , Right Shoulder Button
        Dpad            , Set Dpad Value (0 = Off, Use DPAD_### Contstants)
        TriggerL        , Left Trigger
        TriggerR        , Right Trigger

    """
        func = getattr(_xinput, 'Set' + control)

        if 'Axis' in control:
            target_type = c_short
            target_value = int(32767 * value)
        elif 'Btn' in control:
            target_type = c_bool
            target_value = bool(value)
        elif 'Trigger' in control:
            target_type = c_byte
            target_value = int(255 * value)
        elif 'Dpad' in control:
            target_type = c_int
            target_value = int(value)

        func(c_uint(self.id), target_type(target_value))


def main():
    cons = []

    while True:
        print('Connecting Controller:')
        try:
            cons.append(vController())
        except MaxInputsReachedError:
            break
        else:
            print('This ID:', cons[-1].id)

        # input('Press enter for next controller...')
        time.sleep(2)

    print('Done, disconnecting controllers.')
    del cons
    print('Available:', [_xinput.isControllerExists(
        c_int(x)) for x in range(1, 5)])
    time.sleep(2)


if __name__ == '__main__':
    main()
