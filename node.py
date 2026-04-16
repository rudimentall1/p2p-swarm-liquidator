import paho.mqtt.client as mqtt
import json
import time
import threading
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import os

TOPIC_STATE = "swarm/state"
TOPIC_CONSENSUS = "swarm/consensus"

class SwarmAgent:
    def __init__(self, agent_id, broker="127.0.0.1", port=1883):
        self.id = agent_id
        self.broker = broker
        self.port = port
        self.role = "follower"
        self.leader = None
        self.running = True
        self.privkey, self.pubkey = self.load_or_generate_keys()
        self.client = mqtt.Client(client_id=agent_id, protocol=mqtt.MQTTv5)
        self.client.username_pw_set(agent_id, agent_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def load_or_generate_keys(self):
        os.makedirs("keys", exist_ok=True)
        priv_path = f"keys/{self.id}_priv.pem"
        pub_path = f"keys/{self.id}_pub.pem"
        
        if os.path.exists(priv_path) and os.path.exists(pub_path):
            with open(priv_path, "rb") as f:
                priv = serialization.load_pem_private_key(f.read(), password=None)
            with open(pub_path, "rb") as f:
                pub = serialization.load_pem_public_key(f.read())
            print(f"[{self.id}] Loaded keys")
        else:
            priv = ed25519.Ed25519PrivateKey.generate()
            pub = priv.public_key()
            with open(priv_path, "wb") as f:
                f.write(priv.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            with open(pub_path, "wb") as f:
                f.write(pub.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
            print(f"[{self.id}] Generated new keys")
        return priv, pub
    
    def sign(self, msg):
        signature = self.privkey.sign(json.dumps(msg).encode())
        return base64.b64encode(signature).decode()
    
    def on_connect(self, client, userdata, flags, rc, properties=None):
        print(f"[{self.id}] Connected to {self.broker}:{self.port}")
        client.subscribe(TOPIC_STATE)
        client.subscribe(TOPIC_CONSENSUS)
        # Отправляем HELLO
        hello = {"type": "HELLO", "agent_id": self.id, "pubkey": self.pubkey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()}
        client.publish(TOPIC_STATE, json.dumps(hello))
        # Запускаем heartbeat
        threading.Thread(target=self.heartbeat, daemon=True).start()
        threading.Thread(target=self.leader_election, daemon=True).start()
    
    def heartbeat(self):
        while self.running:
            time.sleep(5)
            msg = {"type": "HEARTBEAT", "agent_id": self.id, "role": self.role}
            msg["signature"] = self.sign(msg)
            self.client.publish(TOPIC_STATE, json.dumps(msg))
            print(f"[{self.id}] Heartbeat sent, role={self.role}")
    
    def leader_election(self):
        peers = {}
        while self.running:
            time.sleep(30)
            # Выбираем лидера по наименьшему ID
            if peers:
                leader = min(peers.keys())
                if self.id == leader:
                    self.role = "leader"
                else:
                    self.role = "follower"
                print(f"[{self.id}] Leader elected: {leader}, my role: {self.role}")
    
    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        print(f"[{self.id}] Received: {payload[:100]}...")
    
    def start(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python node.py <agent_id>")
        sys.exit(1)
    agent = SwarmAgent(sys.argv[1])
    agent.start()
