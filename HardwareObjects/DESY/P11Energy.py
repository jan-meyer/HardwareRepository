
from HardwareRepository.HardwareObjects.abstract.AbstractEnergy import AbstractEnergy
from HardwareRepository.HardwareObjects.mockup.ActuatorMockup import ActuatorMockup

import logging

log= logging.getLogger("HWR")


class P11Energy(AbstractEnergy):
    
    _default_energy = 12.0


    def __init__(self, name):
        super(P11Energy,self).__init__(name)
        self._energy_value = None
        self._state = None

    def init(self):
        self.chan_energy = self.get_channel_object("chanEnergy")
        if self.chan_energy is not None:
            self.chan_energy.connectSignal("update", self.energy_position_changed)

        self.chan_status = self.get_channel_object("chanStatus")
        if self.chan_status is not None:
            self.chan_status.connectSignal("update", self.energy_state_changed)


    def is_ready(self):
        return self._state == self.STATES.READY

    def energy_state_changed(self, state):
        _state = str(state)

        log.debug("P11Energy - energy state changed. it is {}".format(_state))

        if _state == 'ON':
            self._state = self.STATES.READY
        elif _state == 'MOVING':
            self._state = self.STATES.BUSY
        elif _state == 'DISABLED':
            self._state = self.STATES.OFF
        else:
            self._state = self.STATES.FAULT

        self.emit("stateChanged", self._state)

    def energy_position_changed(self, pos):
        """
        Event called when energy value has been changed
        :param pos: float
        :return:
        """
        energy = pos / 1000.0


        if self._energy_value is None or abs(energy - self._energy_value) > 1e-3:
            log.debug("P11Energy - energy value changed. New value is {}".format(energy))
            self._energy_value = energy
            self._wavelength_value = 12.3984 / energy
            if self._wavelength_value is not None:
                self.emit("energyChanged", (self._energy_value, self._wavelength_value))
                self.emit("valueChanged", (self._energy_value,))

    def _set_value(self, bla):
        pass

    def get_value(self):
        """
        Returns current energy in keV
        :return: float
        """

        value = self._default_energy
        if self.chan_energy is not None:
            try:
                value = self.chan_energy.getValue()
                return value / 1000
            except BaseException:
                logging.getLogger("HWR").exception(
                    "Energy: could not read current energy"
                )
                return None
        return value

    def get_limits(self):
        my_limits = (5,14)
        log.debug("EnergyMockup. they asked me for my limits %s" % str(my_limits))
        return my_limits


def test_hwo(hwo):
    print( "Energy is: {0} keV".format(hwo.get_value()))
