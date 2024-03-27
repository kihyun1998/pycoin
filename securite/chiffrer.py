
import json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

filename = 'key/key.json'

# Charger les donnees
with open(filename, 'r') as file:
    donnees = json.load(file)

donnees_bytes = json.dumps(donnees).encode('utf-8')


# Charger la cle publique
with open("cles/cle_publique.pem","rb") as f:
    cle_publique = serialization.load_pem_public_key(
        f.read(),
        backend=default_backend()
    )

# Chiffrer le donnees
chiffre = cle_publique.encrypt(
    donnees_bytes,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Enregistrez les donnees cryptes
with open("key/chiffrer_donnees.bin","wb") as f:
    f.write(chiffre)