from cheby.hdl.wbbus import WBBus
from cheby.hdl.cernbus import CERNBEBus
from cheby.hdl.srambus import SRAMBus
from cheby.hdl.axi4litebus import AXI4LiteBus
from cheby.hdl.avalonbus import AvalonBus


def name_to_busgen(name):
    if name.startswith('wb-'):
        return WBBus(name)
    elif name == 'axi4-lite-32':
        return AXI4LiteBus(name)
    elif name == 'avalon-lite-32':
        return AvalonBus(name)
    elif name.startswith('cern-be-vme-'):
        return CERNBEBus(name)
    elif name == 'sram':
        return SRAMBus(name)
    else:
        raise AssertionError("Unhandled bus '{}'".format(name))
