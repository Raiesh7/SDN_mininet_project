from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import SingleSwitchTopo
import re

def extract_loss(output):
    match = re.search(r'([\d\.]+)% packet loss', output)
    if match:
        return float(match.group(1))
    return None


def run_test():
    print("Starting Mininet (Python API)...")

    topo = SingleSwitchTopo(k=3)
    net = Mininet(topo=topo, controller=RemoteController)

    net.start()

    h1, h2, h3 = net.get('h1', 'h2', 'h3')

    print("Running tests...")

    # Normal traffic
    out1 = h1.cmd("ping -c 20 10.0.0.2")

    # High traffic
    out2 = h1.cmd("ping -i 0.1 -c 30 10.0.0.2")

    # Other flow
    out3 = h2.cmd("ping -c 20 10.0.0.3")

    net.stop()

    return out1, out2, out3


def analyze(out1, out2, out3):
    print("\nAnalyzing results...\n")

    print("---- RAW OUTPUT ----")
    print(out1)
    print(out2)
    print(out3)
    print("--------------------\n")

    loss1 = extract_loss(out1)
    loss2 = extract_loss(out2)
    loss3 = extract_loss(out3)

    print(f"Normal traffic (h1→h2): {loss1}%")
    print(f"High traffic (h1→h2): {loss2}%")
    print(f"Other flow (h2→h3): {loss3}%")

    if loss1 is not None and loss2 is not None and loss3 is not None:
        if loss2 > loss1 and loss3 == 0:
            print("\nADAPTIVE REGRESSION TEST PASSED")
        else:
            print("\nADAPTIVE REGRESSION TEST FAILED")
    else:
        print("\nCould not parse results")


if __name__ == "__main__":
    out1, out2, out3 = run_test()
    analyze(out1, out2, out3)
