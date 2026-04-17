from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import ipv4, arp
import random
import time

log = core.getLogger()

# Traffic tracking
packet_count = {}
start_time = time.time()

BASE_DROP = 0.1   # minimum drop
MAX_DROP = 0.6    # max drop
THRESHOLD = 20    # packets for high traffic

def get_drop_probability(src):
    count = packet_count.get(src, 0)

    if count < THRESHOLD:
        return BASE_DROP
    else:
        return min(MAX_DROP, BASE_DROP + (count / 100))


def _handle_PacketIn(event):
    packet = event.parsed

    # Always allow ARP
    if packet.find('arp'):
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(msg)
        return

    ip = packet.find('ipv4')
    if not ip:
        return

    src = str(ip.srcip)
    dst = str(ip.dstip)

    # 🔹 Count packets per source
    packet_count[src] = packet_count.get(src, 0) + 1

    drop_prob = get_drop_probability(src)

    # Apply only for h1 -> h2
    if src == "10.0.0.1" and dst == "10.0.0.2":

        if random.random() < drop_prob:
            log.info(f"[DROP] {src}->{dst} | Prob={drop_prob:.2f}")
            return
        else:
            log.info(f"[FORWARD] {src}->{dst} | Prob={drop_prob:.2f}")

    # Forward packet
    msg = of.ofp_packet_out()
    msg.data = event.ofp
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    event.connection.send(msg)


def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    log.info("Adaptive Packet Loss Simulator Started")
