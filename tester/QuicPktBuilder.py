import scapy
import scapy.layers
from scapy.layers.inet import IP, UDP, Ether
from scapy.all import Raw, hexdump


TYPE_INITIAL = 0b00

def buildInitialForceVersionNegotiation(sip, dip, sport, dport):
    payload = b"\x00" * 1200
    quic = longheader(TYPE_INITIAL, bytes.fromhex("0A0A0A0A"), bytes.fromhex("1000000000000000"), bytes.fromhex("2000000000000000"), bytes.fromhex(""), len(payload) + 1, bytes.fromhex("00"), payload)
    pkt: scapy.packet.Packet = Ether() / IP(src=sip, dst=dip) / UDP(sport=sport, dport=dport) / Raw(load=quic)
    return pkt


def longheader(pktType, version, dcid, scid, token, length, packetNumber, payload):
    # | long header 1 | fixed bit 1 | pktType 2 | reserved 2 | packet number length 2 |
    firstByte = (0b11000000) | (pktType & 0b00000011) << 4 | (len(packetNumber) - 1 & 0b00000011)
    dcidBytes = len(dcid).to_bytes(1, byteorder="big") + dcid
    scidBytes = len(scid).to_bytes(1, byteorder="big") + scid
    tokenBytes = varInt(len(token)) + token
    lengthBytes = varInt(length)

    header = firstByte.to_bytes(1, byteorder="big") + version + dcidBytes + scidBytes + tokenBytes + lengthBytes + packetNumber + payload
    return header


def varInt(x: int):
    if x < 64:
        result = 0x00 | (x & 0x3F)
        length = 1
    elif x < 16384:
        result = 0x4000 | (x & 0x3FFF)
        length = 2
    elif x < 1073741824:
        result = 0x80000000 | (x & 0x3FFFFFFF)
        length = 4
    else:
        result = 0xC000000000000000 | (x & 0x3FFFFFFFFFFFFFFF)
        length = 8
    return result.to_bytes(length, byteorder="big")


if __name__ == "__main__":
    pkt = buildInitialForceVersionNegotiation("127.0.0.1", "127.0.0.2", 1234, 1234)
    hexdump(pkt)
