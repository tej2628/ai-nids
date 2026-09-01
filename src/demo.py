import random, threading, time
from src.utils import logger


def synthetic_flow():
    attack = random.random() < .32
    return {"source_ip":f"192.168.1.{random.randint(2,254)}","destination_ip":"10.0.0.10","protocol":random.choice(["TCP","UDP"]),"source_port":random.randint(1024,65535),"destination_port":random.choice([80,443,53,22]),"flow_duration":random.uniform(.1, 45 if not attack else 4),"total_packets":random.randint(3,180 if not attack else 25),"total_bytes":random.randint(300,50000 if not attack else 5000),"packet_rate":random.uniform(1,25 if not attack else 200),"service":random.choice(["http","https","dns"] if not attack else ["unknown","dns"])}


class DemoRunner:
    def __init__(self, detector): self.detector, self.running, self.thread = detector, False, None
    def start(self):
        if self.running: return
        self.running=True
        def work():
            while self.running:
                try: self.detector.analyse(synthetic_flow(), "DEMO")
                except Exception:
                    logger.exception("Demo prediction failed")
                time.sleep(1.2)
        self.thread=threading.Thread(target=work, daemon=True); self.thread.start()
    def stop(self): self.running=False
