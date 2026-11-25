"""make.fun news-image-20261125 entry point.

The image is already finished and committed as frontpage.png beside
this file. All this module does is hand that exact file to the grader:
it checks the file really is a PNG under the 1 MiB cap, copies it to
the output directory, and confirms the copy is byte for byte the same.
It never touches the network and never changes a pixel.
"""
import hashlib, os, sys

IMAGE_FILE = "frontpage.png"
OUTPUT_FILE = "entry.png"
SIZE_LIMIT = 1048576
HEADER = bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A))


def die(reason):
    sys.stderr.write("entry failed: " + reason + "\n")
    sys.exit(1)


def load_image():
    base = os.path.dirname(os.path.realpath(__file__))
    found = os.path.join(base, IMAGE_FILE)
    if not os.path.isfile(found):
        die("missing " + IMAGE_FILE + " beside this program")
    with open(found, "rb") as stream:
        payload = stream.read()
    if len(payload) > SIZE_LIMIT:
        die(IMAGE_FILE + " is over the 1 MiB size limit")
    if payload[0:8] != HEADER:
        die(IMAGE_FILE + " does not begin with a PNG header")
    return payload


def save_image(payload):
    folder = os.getenv("MAKEFUN_OUTPUT_DIR", "/output") or "/output"
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError:
        die("cannot create output folder " + folder)
    target = os.path.join(folder, OUTPUT_FILE)
    with open(target, "wb") as stream:
        stream.write(payload)
    with open(target, "rb") as stream:
        if stream.read() != payload:
            die("output copy differs from " + IMAGE_FILE)
    return target


def run():
    payload = load_image()
    target = save_image(payload)
    checksum = hashlib.sha256(payload).hexdigest()
    sys.stdout.write(target + ": " + str(len(payload)) +
                     " bytes, sha256 " + checksum + "\n")


if __name__ == "__main__":
    run()
