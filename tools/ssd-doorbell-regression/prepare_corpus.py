import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

import pymupdf
from pypdf import PdfReader

from benchmark import PAGE_COUNTS, PCIE, ROOT, norm
from retrieval_trial import NVME_PAGES

NVME_PDF = ".kb_index/spec_eval/nvme-official-full.pdf"
COVERS = {"pcie": "revision 5 0 version 1 0", "nvme": "revision 2 1"}


def prepare(pcie, nvme, destination):
    if destination.exists():
        raise FileExistsError(f"Use a new corpus directory. {destination} already exists.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    sources = {"pcie": pcie, "nvme": nvme}
    with TemporaryDirectory(prefix="spec-corpus-", dir=destination.parent) as temporary:
        corpus = Path(temporary) / "corpus"
        hashes = {}
        for protocol, original in sources.items():
            stored = corpus / (PCIE if protocol == "pcie" else NVME_PDF)
            stored.parent.mkdir(parents=True, exist_ok=True)
            copyfile(original, stored)
            with stored.open("rb") as file:
                hashes[protocol] = hashlib.file_digest(file, "sha256").hexdigest()
            with pymupdf.open(stored) as document:
                if len(document) != PAGE_COUNTS[protocol] or COVERS[protocol] not in norm(document[0].get_text()):
                    raise ValueError(f"Unexpected {protocol} PDF edition")
                if protocol == "nvme":
                    extract_nvme(stored, document.get_toc(), corpus / NVME_PAGES)
        (corpus / "source-hashes.json").write_text(
            json.dumps(hashes, indent=2) + "\n", encoding="utf-8",
        )
        corpus.rename(destination)
    return hashes


def extract_nvme(source, outline, output):
    output.mkdir(parents=True)
    bookmarks = defaultdict(list)
    for _, title, number in outline:
        bookmarks[number].append(title)
    with source.open("rb") as file:
        write_nvme_pages(PdfReader(file).pages, bookmarks, output)


def write_nvme_pages(pages, bookmarks, output):
    for number, page in enumerate(pages, 1):
        headings = repr(bookmarks[number])
        text = "\n".join(line.rstrip() for line in page.extract_text().splitlines()).strip()
        content = f"---\npage: {number}\nheadings: {headings}\n---\n\n# Source page {number}\n\n{text}\n"
        (output / f"page-{number:03}.md").write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Prepare the local SSD evaluation corpus from two PDF files.")
    parser.add_argument("--pcie", type=Path, required=True)
    parser.add_argument("--nvme", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        hashes = prepare(args.pcie, args.nvme, args.output.resolve())
    except (OSError, ValueError, RuntimeError) as error:
        parser.error(str(error))
    print(json.dumps(hashes, indent=2))


if __name__ == "__main__":
    main()
