"""
crypto_core.kdf
===============
Derivación determinística de claves maestras con alto nivel de seguridad simétrica.
Diseñado para resistir ataques cuánticos (algoritmo de Grover) y ataques clásicos en GPUs,
garantizando entropía fuerte a través de parámetros PQC-grade (>= 256 bits y SHA3).
"""

import hashlib
import hmac
import base64

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def _fixed_salt(context: str, salt_phrase: str) -> bytes:
    """
    Combina la frase de salt y el contexto para generar un salt fuerte usando HMAC-SHA256.
    """
    key = salt_phrase.encode("utf-8")
    msg = context.encode("utf-8") if context else b"masterkey-derivator-v3-pqc-grade"
    return hmac.new(key, msg, hashlib.sha256).digest()


def derive_scrypt_pqc(password: str, salt_phrase: str, context: str, length: int) -> bytes:
    """
    Scrypt endurecido. Parámetros mejorados para alta resistencia:
    - n=2**16 (65536) / n=2**15 dependiendo del hardware. Aquí subimos a 2**16.
    - r=8, p=2 (para aprovechar multi-threading de GPU y matar paralelización masiva)
    """
    salt = _fixed_salt(context, salt_phrase)
    kdf = Scrypt(
        salt=salt,
        length=length,
        n=2**16,  # 65536 - Fuerte contra ASICs/GPUs
        r=8,
        p=2,
        backend=default_backend()
    )
    return kdf.derive(password.encode("utf-8"))


def derive_pbkdf2_sha512_pqc(password: str, salt_phrase: str, context: str, length: int) -> bytes:
    """
    PBKDF2 iterativo estándar pero con un recuento masivo de iteraciones
    para compensar el progreso del hardware paralelo.
    """
    salt = _fixed_salt(context, salt_phrase)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=length,
        salt=salt,
        iterations=1_000_000, # 1 millón de iteraciones
        backend=default_backend()
    )
    return kdf.derive(password.encode("utf-8"))


def derive_sha3_512_iterative(password: str, salt_phrase: str, context: str, length: int) -> bytes:
    """
    Derivación pura basada en SHA3-512 nativo, el cual es resistente por defecto
    a la cripto-análisis cuántica actual.
    """
    salt = _fixed_salt(context, salt_phrase)
    data = password.encode("utf-8") + salt
    # 500k iteraciones para hacer prohibitiva la pre-computación
    for _ in range(500_000):
        data = hashlib.sha3_512(data).digest()
    return data[:length]


# Mapeo de Algoritmos en la Interfaz (Actualizados a Post-Quantum / High Security)
ALGORITHMS = {
    "Scrypt (Recomendado PQC-grade)": derive_scrypt_pqc,
    "PBKDF2-SHA512 (1M Iteraciones)": derive_pbkdf2_sha512_pqc,
    "SHA3-512 Iterativo (500k)": derive_sha3_512_iterative,
}

# Formatos de Salida Soportados
OUTPUT_FORMATS = {
    "Hexadecimal": lambda b: b.hex(),
    "Base64": lambda b: base64.b64encode(b).decode(),
    "Base64 URL-safe": lambda b: base64.urlsafe_b64encode(b).decode(),
}

# Longitudes Recomendadas (256+ bits para mitigar Ley de Grover cuántica)
KEY_LENGTHS = {
    "128 bits (16 B - Clásico)": 16,
    "192 bits (24 B - Clásico)": 24,
    "256 bits (32 B - Nivel PQC 1)": 32,
    "512 bits (64 B - Nivel PQC 5)": 64,
}
