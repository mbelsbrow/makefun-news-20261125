"""make.fun news-image-20261125 entry point.

The finished front page is already committed as frontpage.png beside
this file. This module simply hands that exact file to the grader: it
validates the file (PNG magic bytes, 1 MiB size cap), copies it to the
output directory as entry.png, and verifies the copy is byte-identical
to the source. It never touches the network and never changes a pixel.
"""

import hashlib
import os
import sys

# --- Configuration -------------------------------------------------------

SOURCE_FILENAME = "frontpage.png"
OUTPUT_FILENAME = "entry.png"
DEFAULT_OUTPUT_DIR = "/output"
OUTPUT_DIR_ENV_VAR = "MAKEFUN_OUTPUT_DIR"

MAX_IMAGE_BYTES = 1024 * 1024  # 1 MiB cap

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

FAILURE_PREFIX = "entry failed: "


# --- Errors --------------------------------------------------------------


class ExportError(Exception):
    """Raised when any step of the export cannot be completed."""


# --- Exporter ------------------------------------------------------------


class FrontPageExporter:
    """Validates frontpage.png and exports an identical copy as entry.png."""

    def __init__(self, source_dir=None, output_dir=None):
        self.source_dir = source_dir or os.path.dirname(
            os.path.realpath(__file__)
        )
        self.output_dir = output_dir or os.environ.get(
            OUTPUT_DIR_ENV_VAR, DEFAULT_OUTPUT_DIR
        ) or DEFAULT_OUTPUT_DIR

    @property
    def source_path(self):
        return os.path.join(self.source_dir, SOURCE_FILENAME)

    @property
    def output_path(self):
        return os.path.join(self.output_dir, OUTPUT_FILENAME)

    def load_source(self):
        """Read and validate frontpage.png; return its bytes."""
        if not os.path.isfile(self.source_path):
            raise ExportError(
                "missing %s beside this program" % SOURCE_FILENAME
            )
        with open(self.source_path, "rb") as handle:
            payload = handle.read()
        self._validate_payload(payload)
        return payload

    def _validate_payload(self, payload):
        if len(payload) > MAX_IMAGE_BYTES:
            raise ExportError(
                "%s is over the 1 MiB size limit" % SOURCE_FILENAME
            )
        if payload[: len(PNG_MAGIC)] != PNG_MAGIC:
            raise ExportError(
                "%s does not begin with a PNG header" % SOURCE_FILENAME
            )

    def write_copy(self, payload):
        """Write payload to the output directory and verify the copy."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except OSError:
            raise ExportError(
                "cannot create output folder %s" % self.output_dir
            )
        with open(self.output_path, "wb") as handle:
            handle.write(payload)
        self._verify_copy(payload)
        return self.output_path

    def _verify_copy(self, payload):
        with open(self.output_path, "rb") as handle:
            if handle.read() != payload:
                raise ExportError(
                    "output copy differs from %s" % SOURCE_FILENAME
                )

    @staticmethod
    def checksum(payload):
        return hashlib.sha256(payload).hexdigest()

    def export(self):
        """Run the full export and return (path, size, sha256)."""
        payload = self.load_source()
        target = self.write_copy(payload)
        return target, len(payload), self.checksum(payload)


# --- Entry point ---------------------------------------------------------


def main(argv=None):
    exporter = FrontPageExporter()
    try:
        target, size, digest = exporter.export()
    except ExportError as exc:
        sys.stderr.write(FAILURE_PREFIX + str(exc) + "\n")
        return 1
    sys.stdout.write(
        "%s: %d bytes, sha256 %s\n" % (target, size, digest)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
