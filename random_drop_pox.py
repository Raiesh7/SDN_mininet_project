from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ipv4
import random

log = core.getLogger()

DROP_PROBABILITY = 0.3

def _handle_ConnectionUp(event):
    log.info("Switch connected - installing default forwarding rule")

    # Install default rule: flood everything
    msg = of.ofp_flow_mod()
    msg.priority = 0
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    event.connection.send(msg)


def _handle_PacketIn(event):
    packet = event.parsed
    ip = packet.find('ipv4')

    if not ip:
        return

    src = ip.srcip
    dst = ip.dstip

    # Apply random drop only for h1 -> h2
    if str(src) == "10.0.0.1" and str(dst) == "10.0.0.2":

        if random.random() < DROP_PROBABILITY:
            log.info(f"[DROP] {src} -> {dst}")
            return  # drop packet only

        else:
            log.info(f"[ALLOW] {src} -> {dst}")

    # Forward packet
    msg = of.ofp_packet_out()
    msg.data = event.ofp
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    event.connection.send(msg)


def launch():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    log.info("Stable Random Packet Loss Simulator Started")
