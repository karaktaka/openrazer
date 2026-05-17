# SPDX-License-Identifier: GPL-2.0-or-later

"""
Module for accessory methods
"""
import time

from openrazer_daemon.dbus_services import endpoint


@endpoint('razer.device.misc', 'setMouseDockProPair', in_sig='s')
def set_mouse_dock_pro_pair(self, pid):
    """
    Pair Mouse Dock Pro with a mouse by PID (hex string, e.g. "00ab")

    :param pid: product id
    :type pid: str
    """
    self.logger.debug("DBus call set_mouse_dock_pro_pair")

    driver_path = self.get_driver_path('pair')

    with open(driver_path, 'w') as driver_file:
        driver_file.write(pid)


@endpoint('razer.device.misc', 'setMouseDockProUnpair', in_sig='s')
def set_mouse_dock_pro_unpair(self, pid):
    """
    Unpair Mouse Dock Pro from a mouse by PID (hex string, e.g. "00ab")

    :param pid: product id
    :type pid: str
    """
    self.logger.debug("DBus call set_mouse_dock_pro_unpair")

    driver_path = self.get_driver_path('unpair')

    with open(driver_path, 'w') as driver_file:
        driver_file.write(pid)


@endpoint('razer.device.misc', 'scanForNearbyMice')
def scan_for_nearby_mice(self):
    """
    Ask the dock to scan for nearby Razer mice.  Discovery announcements
    arrive on the dock's interrupt endpoint and populate the kernel cache
    within a few hundred milliseconds.  The dock's scan is one-shot, so
    callers that want fresh results should call this before reading
    getNearbyMice.
    """
    self.logger.debug("DBus call scan_for_nearby_mice")

    with open(self.get_driver_path('scan_for_mice'), 'w') as driver_file:
        driver_file.write('1')


@endpoint('razer.device.misc', 'getNearbyMice', out_sig='as')
def get_nearby_mice(self):
    """
    List PIDs of Razer mice the dock has seen on its RF channel recently.

    The driver caches the most recent discovery report and ages it out after
    30 seconds.  Call scanForNearbyMice first if you want fresh results — the
    dock does not beacon continuously.

    :return: list of 4-hex-digit mouse PID strings (e.g. ["00ab"])
    :rtype: list[str]
    """
    self.logger.debug("DBus call get_nearby_mice")

    with open(self.get_driver_path('nearby_mice'), 'r') as driver_file:
        return driver_file.read().split()


@endpoint('razer.device.misc', 'pairAnyNearbyMouse', out_sig='s')
def pair_any_nearby_mouse(self):
    """
    Trigger a fresh scan, wait for results, and pair the first mouse the dock
    sees.  Convenience method for a one-click "scan and pair" UX where the
    caller does not need to know the PID upfront.

    :return: PID of the mouse that was paired, or "" if none were in range
    :rtype: str
    """
    self.logger.debug("DBus call pair_any_nearby_mouse")

    scan_for_nearby_mice(self)
    # Dock typically emits its first announcement within ~5 ms of the scan
    # request (per v2 capture); 500 ms is generous and bounded.
    time.sleep(0.5)

    pids = get_nearby_mice(self)
    if not pids:
        return ''

    set_mouse_dock_pro_pair(self, pids[0])
    return pids[0]


@endpoint('razer.device.misc.mug', 'isMugPresent', out_sig='b')
def is_mug_present(self):
    """
    Get if the mug is present

    :return: True if there's a mug
    :rtype: bool
    """
    self.logger.debug("DBus call is_mug_present")

    driver_path = self.get_driver_path('is_mug_present')

    with open(driver_path, 'r') as driver_file:
        return int(driver_file.read().strip()) == 1
