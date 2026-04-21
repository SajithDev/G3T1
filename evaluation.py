import time
import random
import string
import os
import matplotlib.pyplot as plt
import importlib

from aes import AES128
from rsa import rsa_encrypt, rsa_decrypt
from vigenere import vigenere_encrypt, vigenere_decrypt

# ---------------- CONFIG ----------------
SIZES = [1024, 10240, 102400]   # 1 KB, 10 KB, 100 KB
RUNS = 5

AES_KEY = b"0123456789abcdef"
DES_KEYS = (b"12345678", b"abcdefgh", b"87654321")
VIG_KEY = "crypto"

RSA_E = 65537
RSA_N = int("87084725150856806800464976057531161251515449715127063102301522640731095387852872686069660800427282811845950854584764844603665596623419079276347597161829006349835945119557872738137438802595005067535758120659737684005980191931356408827586327014874973293486406345506089327873020526682989479323926677339226544763")
RSA_D = int("11832849801919219136642516621028045088190565325132467109052826023707377579517369291689432372977172489425640361323791613000223417885035123685183565813602806584464831763222157749154202032683624276745171393192450779783626074207589769384079019717609899059821574183714204133531155597547467950741133611295804118193")
# ---------------------------------------


def avg(times):
    return sum(times) / len(times)


def measure(fn):
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)  # seconds
    return avg(times)


def throughput(bytes_processed, seconds):
    return (bytes_processed / 1024) / seconds if seconds > 0 else 0


# ---------- INPUT GENERATION ----------

def random_bytes(size):
    return os.urandom(size)


def random_text(size):
    alphabet = string.ascii_lowercase
    return "".join(random.choice(alphabet) for _ in range(size))


# ---------- BENCHMARK ----------

def run():
    results = {
        "AES": [],
        "3DES": [],
        "RSA": [],
        "Vigenere": [],
    }

    aes = AES128(AES_KEY)
    des = importlib.import_module("3des")

    # -------- AES --------
    print("\n=== AES ===")
    for size in SIZES:
        data = random_bytes(size)

        enc_fn = lambda: aes.encrypt(data)
        ciphertext = enc_fn()
        dec_fn = lambda: aes.decrypt(ciphertext)

        t_enc = measure(enc_fn)
        t_dec = measure(dec_fn)

        thr_enc = throughput(size, t_enc)
        thr_dec = throughput(size, t_dec)

        results["AES"].append((size, t_enc * 1000, t_dec * 1000))

        print(f"{size} bytes | enc={t_enc*1000:.2f} ms ({thr_enc:.2f} KB/s) "
              f"| dec={t_dec*1000:.2f} ms ({thr_dec:.2f} KB/s)")

    # -------- 3DES --------
    print("\n=== 3DES ===")
    for size in SIZES:
        data = random_bytes(size)

        enc_fn = lambda: des.encrypt_3des(data, *DES_KEYS)
        ciphertext = enc_fn()
        dec_fn = lambda: des.decrypt_3des(ciphertext, *DES_KEYS)

        t_enc = measure(enc_fn)
        t_dec = measure(dec_fn)

        thr_enc = throughput(size, t_enc)
        thr_dec = throughput(size, t_dec)

        results["3DES"].append((size, t_enc * 1000, t_dec * 1000))

        print(f"{size} bytes | enc={t_enc*1000:.2f} ms ({thr_enc:.2f} KB/s) "
              f"| dec={t_dec*1000:.2f} ms ({thr_dec:.2f} KB/s)")

    # -------- RSA --------
    print("\n=== RSA ===")
    for size in SIZES:
        data = random_bytes(size)

        enc_fn = lambda: rsa_encrypt(data, RSA_E, RSA_N)
        ciphertext = enc_fn()
        dec_fn = lambda: rsa_decrypt(ciphertext, RSA_D, RSA_N)

        t_enc = measure(enc_fn)
        t_dec = measure(dec_fn)

        thr_enc = throughput(size, t_enc)
        thr_dec = throughput(size, t_dec)

        results["RSA"].append((size, t_enc * 1000, t_dec * 1000))

        print(f"{size} bytes | enc={t_enc*1000:.2f} ms ({thr_enc:.2f} KB/s) "
              f"| dec={t_dec*1000:.2f} ms ({thr_dec:.2f} KB/s)")

    # -------- Vigenere --------
    print("\n=== Vigenere ===")
    for size in SIZES:
        text = random_text(size)

        enc_fn = lambda: vigenere_encrypt(text, VIG_KEY)
        ciphertext = enc_fn()
        dec_fn = lambda: vigenere_decrypt(ciphertext, VIG_KEY)

        t_enc = measure(enc_fn)
        t_dec = measure(dec_fn)

        thr_enc = throughput(size, t_enc)
        thr_dec = throughput(size, t_dec)

        results["Vigenere"].append((size, t_enc * 1000, t_dec * 1000))

        print(f"{size} bytes | enc={t_enc*1000:.2f} ms ({thr_enc:.2f} KB/s) "
              f"| dec={t_dec*1000:.2f} ms ({thr_dec:.2f} KB/s)")

    return results


# ---------- PLOTTING ----------

def plot(results):
    # Encryption plot
    plt.figure()
    for algo, data in results.items():
        sizes = [x[0] for x in data]
        enc = [x[1] for x in data]
        plt.plot(sizes, enc, marker="o", label=algo)

    plt.xscale("log")
    plt.xlabel("Input size (bytes)")
    plt.ylabel("Encryption Time (ms)")
    plt.title("Encryption Benchmark")
    plt.legend()
    plt.grid(True)
    plt.savefig("encryption_plot.png")
    plt.close()

    # Decryption plot
    plt.figure()
    for algo, data in results.items():
        sizes = [x[0] for x in data]
        dec = [x[2] for x in data]
        plt.plot(sizes, dec, marker="x", linestyle="--", label=algo)

    plt.xscale("log")
    plt.xlabel("Input size (bytes)")
    plt.ylabel("Decryption Time (ms)")
    plt.title("Decryption Benchmark")
    plt.legend()
    plt.grid(True)
    plt.savefig("decryption_plot.png")
    plt.close()


if __name__ == "__main__":
    results = run()
    plot(results)