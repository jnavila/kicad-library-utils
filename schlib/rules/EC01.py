# -*- coding: utf-8 -*-

from rules.rule import *
import re

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'EC01 - Extra Checking',
                                   'Check pins names against pin types.')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * probably_wrong_pin_types
            * double_inverted_pins
        """
        self.probably_wrong_pin_types = []
        self.double_inverted_pins = []
        for pin in self.component.pins:
            if ('GND' in pin['name'].upper() or
                'VCC' in pin['name'].upper() or
                'VDD' in pin['name'].upper()):
                if pin['electrical_type'] != 'W':
                    self.probably_wrong_pin_types.append(pin)
                    self.verboseOut(Verbosity.HIGH,Severity.WARNING,'pin {0} ({1}): {2} ({3}), expected: W ({4})'.format(pin['name'], pin['num'], pin['electrical_type'],pinElecticalTypeToStr(pin['electrical_type']),pinElecticalTypeToStr("W")))

            # check if name contains overlining
            m = re.search('(\~)(.+)', pin['name'])
            if m and pin['pin_type'] == 'I':
                self.double_inverted_pins.append(pin)
                self.verboseOut(Verbosity.HIGH,Severity.WARNING,'pin {0} ({1}): double inversion (overline + pin type:Inverting)'.format(pin['name'], pin['num']))

        return False if len(self.probably_wrong_pin_types)+len(self.double_inverted_pins) == 0 else True

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.verboseOut(Verbosity.HIGH, Severity.INFO,"Fixing...")
        for pin in self.probably_wrong_pin_types:
            pin['electrical_type'] = 'W'

        for pin in self.double_inverted_pins:
            pin['pin_type']="" #reset pin type (removes dot at the base of pin)

        self.recheck()
