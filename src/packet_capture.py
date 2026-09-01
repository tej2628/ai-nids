import threading
from src.utils import logger


class PacketMonitor:
    def __init__(self, detector): self.detector, self.running, self.thread, self.error = detector, False, None, None
    def start(self):
        if self.running: return
        try:
            from scapy.all import sniff, IP, TCP, UDP
        except ImportError as exc:
            raise RuntimeError("Scapy is unavailable. Install requirements and Npcap on Windows.") from exc
        self.running, self.error = True, None
        def handle(packet):
            if not self.running or not packet.haslayer(IP): return
            proto, sport, dport = "IP", 0, 0
            if packet.haslayer(TCP): proto, sport, dport = "TCP", int(packet[TCP].sport), int(packet[TCP].dport)
            elif packet.haslayer(UDP): proto, sport, dport = "UDP", int(packet[UDP].sport), int(packet[UDP].dport)
            flow={"source_ip":packet[IP].src,"destination_ip":packet[IP].dst,"protocol":proto,"source_port":sport,"destination_port":dport,"flow_duration":1,"total_packets":1,"total_bytes":len(packet),"packet_rate":1,"service":"unknown"}
            try: self.detector.analyse(flow, "LIVE")
            except Exception: logger.exception("Live prediction failed")
        def worker():
            try: sniff(prn=handle, store=False, stop_filter=lambda _: not self.running)
            except Exception as exc: self.error=str(exc); self.running=False; logger.exception("Packet capture failed")
        self.thread=threading.Thread(target=worker, daemon=True); self.thread.start()
    def stop(self): self.running=False
