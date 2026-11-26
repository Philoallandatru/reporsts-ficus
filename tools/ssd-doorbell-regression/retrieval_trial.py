"""Offline, version-scoped page retrieval for the PCIe 5.0 and NVMe 2.1 benchmark."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sqlite3
import tempfile
import unicodedata
from collections import Counter, defaultdict
from contextlib import closing
from math import log1p
from pathlib import Path


PCIE_PDF = "kb/pcie/PCI Express Base Specification.pdf"
NVME_PAGES = "kb/nvme/_source/pages"
MODES = ("bm25", "expanded", "domain", "fusion", "refined")
PROTOCOLS = ("pcie", "nvme")
STOP = set("a an and are as at be can does for from how if in is it of on or should than that the their this to under what when where which will with would".split())
WORD = re.compile(r"[A-Za-z0-9]+")
SYMBOL = re.compile(r"(?<![A-Za-z0-9])[A-Za-z][A-Za-z0-9]*(?:[./-][A-Za-z0-9]+)+")
ENGLISH_SPAN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[ ./-]+[A-Za-z0-9]+){1,5}")



GLOSSARY = {
    "主机": "host", "控制器": "controller", "命名空间": "namespace", "名字空间": "namespace",
    "提交队列": "submission queue", "完成队列": "completion queue", "管理队列": "admin queue",
    "队列": "queue", "门铃": "doorbell", "中断": "interrupt", "向量": "vector",
    "子系统": "subsystem", "标识符": "identifier", "标识": "identify", "描述符": "descriptor",
    "元数据": "metadata", "持久": "persistent", "保留": "reserved", "寄存器": "register",
    "异步事件": "asynchronous event", "原子": "atomic", "激活": "activation",
    "特性": "feature", "日志": "log", "固件": "firmware", "遥测": "telemetry",
    "读写": "read write", "读取": "read", "写入": "write", "缓冲区": "buffer",
    "缓存": "cache", "刷新": "flush", "仲裁": "arbitration", "优先级": "priority",
    "映射": "mapping", "列表": "list", "开启": "enable", "使能": "enable",
    "禁用": "disable", "初始化": "initialization", "关机": "shutdown", "关闭": "shutdown",
    "重置": "reset", "复位": "reset", "超时": "timeout", "附加": "attachment",
    "分离": "detach", "创建": "create", "删除": "delete", "能力": "capability",
    "上电": "power on", "掉电": "power loss", "电源": "power", "功耗": "power",
    "错误": "error", "不可纠正": "uncorrectable", "可纠正": "correctable",
    "状态码": "status code", "状态": "status", "传输": "transfer", "协议": "protocol",
    "带宽": "bandwidth", "速率": "rate", "地址": "address", "对齐": "alignment",
    "偏移": "offset", "粒度": "granularity", "页大小": "page size", "字节": "byte",
    "内存": "memory", "配置空间": "configuration space", "配置": "configuration",
    "端点": "endpoint", "根端口": "root port", "根复合体": "root complex",
    "上游": "upstream", "下游": "downstream", "端口": "port", "交换机": "switch",
    "虚拟通道": "virtual channel", "流量类别": "traffic class", "流控": "flow control",
    "流控制": "flow control", "信用": "credit", "重传": "replay", "重试": "retry",
    "链路": "link", "训练": "training", "均衡": "equalization", "接收方": "receiver",
    "接收端": "receiver", "发送方": "transmitter", "发送端": "transmitter",
    "事务层": "transaction layer", "数据链路层": "data link layer", "物理层": "physical layer",
    "请求者": "requester", "请求方": "requester", "完成者": "completer", "完成方": "completer",
    "报文": "packet", "前缀": "prefix", "载荷": "payload", "负载": "payload",
    "排序": "ordering", "顺序": "ordering", "序列号": "sequence number", "标签": "tag",
    "路由": "routing", "功能": "function", "设备": "device", "消息": "message",
    "毒化": "poisoned", "畸形": "malformed", "热插拔": "hot plug", "唤醒": "wake",
    "清理": "sanitize", "保留区": "reserved", "预留": "reservation", "预约": "reservation",
    "逻辑块": "logical block", "扇区": "sector", "介质": "media", "擦除": "erase",
}
ACRONYMS = {
    "sq": "submission queue", "cq": "completion queue", "sqe": "submission queue entry",
    "cqe": "completion queue entry", "nsid": "namespace identifier",
    "rc": "root complex", "ep": "endpoint", "vc": "virtual channel", "tc": "traffic class",
    "dllp": "data link layer packet", "tlp": "transaction layer packet",
    "fc": "flow control", "aspm": "active state power management",
}


def query_expression(query, aliases, expanded):
    query = unicodedata.normalize("NFKC", query)
    raw = WORD.findall(query)
    words = [w.lower() for w in raw if w.lower() not in STOP]
    phrases = []
    if expanded:
        phrases.extend(m.group(0) for m in SYMBOL.finditer(query))
        phrases.extend(m.group(0) for m in ENGLISH_SPAN.finditer(query))
        phrases.extend(aliases[word] for word in aliases if word in query)
        phrases.extend(ACRONYMS[w] for w in words if w in ACRONYMS)
    parts = dict.fromkeys(words)
    for phrase in phrases:
        tokens = [w.lower() for w in WORD.findall(phrase)]
        for word in tokens:
            if word not in STOP:
                parts[word] = None
        if 1 < len(tokens) <= 8:
            parts[" ".join(tokens)] = None
    return " OR ".join(f'"{part}"' for part in parts)


def nvme_page(path):
    text = path.read_text(encoding="utf-8-sig")
    header, separator, body = text.partition("\n---\n")
    if not separator:
        raise ValueError(f"Missing source front matter in {path}")
    title = re.search(r"^headings: (.*)$", header, re.M)
    headings = ast.literal_eval(title[1]) if title else []
    body = re.sub(r"^\s*# Source page \d+\s*\n", "", body)
    return headings, body.strip()


def windows(body, size=90, stride=65):
    words = body.split()
    for start in range(0, len(words), stride):
        yield " ".join(words[start:start + size])
        if start + size >= len(words):
            break


CAPTION = re.compile(r"^\s*(?:Figure|Table)\s+\d+(?:[-–.]\d+)*\s*[:.—–-]\s*\S", re.I)
VALUE_HEADER = re.compile(r"^\s*(?:Values?|Encodings?|Codes?)\s+(?:Definitions?|Descriptions?|Meanings?)\b", re.I)
CODE = r"(?:[0-9A-F]+h|[01]+b)"
VALUE_ROW = re.compile(rf"^\s*({CODE}(?:\s*(?:to|through|[-–])\s*{CODE})?)(?=\s|$)", re.I)
PRINTED_TABLE = re.compile(r"^Table \d+[-–]\d+\s+[A-Z0-9]")
VERTICAL_ROW = re.compile(rf"^\s*({CODE}(?:\s*(?:to|through|[-–])\s*{CODE})?|[01]{{2,8}})\s*$", re.I)
FIELD_LINE = re.compile(r"^\s*(?:\d+(?::\d+)?(?:\s+Reserved)?|(?:Bits?|Bytes?)\s+Description|Notes?:)\s*$", re.I)
CONDITION = re.compile(r"(?:^|[.!?]\s+)(?:If |When |While |Unless |Prior to |Before |After |Only (?:when|if) |For .*?\bwhile )", re.I)


def page_outcomes(body, bookmarks):
    lines = body.splitlines()
    sections = {entry["line"] - 1 for entry in bookmarks if entry.get("line")}
    structures = sections | {i for i, line in enumerate(lines)
                             if CAPTION.match(line) or PRINTED_TABLE.match(line) or FIELD_LINE.fullmatch(line)}
    groups = []
    for header, line in enumerate(lines):
        vertical = bool(PRINTED_TABLE.match(line))
        if vertical:
            start = next((j for j in range(header + 1, min(len(lines), header + 8))
                          if VERTICAL_ROW.match(lines[j])), None)
            if start is None or any(not lines[i].strip() or PRINTED_TABLE.match(lines[i])
                                    for i in range(header + 1, start)):
                continue
            pattern = VERTICAL_ROW
        elif VALUE_HEADER.match(line):
            start = header + 1
            pattern = VALUE_ROW
        else:
            continue
        if start >= len(lines) or not pattern.match(lines[start]):
            continue
        rows = []
        for i in range(start, len(lines)):
            line = lines[i].strip()
            match = pattern.match(line)
            if (not line or (i in structures and not match) or VALUE_HEADER.match(line)
                    or line.startswith("5.0-1.0-PUB")):
                break
            if match:
                rows.append([match[1], i + 1, i + 1])
            elif line.lower().startswith(("if ", "when ")) and lines[i - 1].rstrip().endswith("."):
                break
            else:
                rows[-1][2] = i + 1
        if not rows or (vertical and len(rows) < 2):
            continue
        end = rows[-1][2]
        field = header if vertical else next((j for j in range(header - 1, max(-1, header - 10), -1)
                                              if re.search(r"\([A-Za-z][\w -]*\)\s*:", lines[j]) or CAPTION.match(lines[j])), header)
        group = {"field_line": field + 1, "field": lines[field].strip(), "header_line": header + 1,
                 "rows": rows}
        if end == len(lines) or (end < len(lines) and lines[end].startswith("5.0-1.0-PUB")):
            group["check_next_page"] = True
        if header < 8 and re.sub(r"[hb]$", "", re.split(r"\s|[-–]", rows[0][0])[0], flags=re.I).strip("0"):
            group["check_previous_page"] = True
        groups.append(group)
    condition_lines = []
    for i, line in enumerate(lines):
        if not CONDITION.search(line.strip()) or i in structures:
            continue
        end = i
        while (end + 1 < len(lines) and end - i < 10 and
               not re.search(r"[.!?;:]\s*$", lines[end]) and end + 1 not in structures and
               lines[end + 1].strip() and not lines[end + 1].startswith("5.0-1.0-PUB")):
            end += 1
        if not condition_lines or end + 1 > condition_lines[-1][1]:
            condition_lines.append([i + 1, end + 1])
    return {"value_tables": groups, "condition_lines": condition_lines}


def heading_line(lines, title, start):
    def key(text):
        return "".join(WORD.findall(unicodedata.normalize("NFKC", text))).casefold()

    bare_title = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", title)
    names = {key(title), key(bare_title)} - {""}
    for i in range(start, len(lines)):
        if any(key(" ".join(lines[i:i + count])) in names for count in (1, 2)):
            if lines[i].strip():
                return i + 1
    return None


def locate_passage(body, preview, expression, bookmarks, budget=1000):
    lines = body.splitlines()
    if not lines or not body.strip():
        return {"passage": "", "lines": None}
    token_lines = [i for i, line in enumerate(lines) for _ in line.split()]
    flat = " ".join(body.split())
    at = flat.find(preview) if preview else -1
    start_word = len(flat[:at].split()) if at >= 0 else 0
    end_word = min(len(token_lines), start_word + max(1, len(preview.split())))
    start, end = token_lines[start_word], token_lines[end_word - 1]
    terms = set(WORD.findall(expression.casefold()))
    matches = [terms.intersection(WORD.findall(line.casefold())) for line in lines]
    freq = Counter(t for group in matches for t in group)
    weights = {t: log1p(len(lines) / n) for t, n in freq.items()}
    center = (start + end) / 2
    peak = max(range(start, end + 1),
               key=lambda i: (sum(weights[t] for t in sorted(matches[i])), -abs(i - center)))
    captions = [i for i, line in enumerate(lines) if CAPTION.match(line)
                and not re.search(r"\.{6}", line)]
    lists = [i for i, line in enumerate(lines) if line.rstrip().endswith(":") and
             re.search(r"\bthe following\b", line, re.I)]
    on_page = [b for b in bookmarks if b.get("line")]
    boundaries = [0, len(lines), *(b["line"] - 1 for b in on_page), *lists, *captions]
    floor = max(pos for pos in boundaries if pos <= peak)
    ceiling = min(pos for pos in boundaries if pos > peak)
    first = last = peak
    before = after = 0
    while True:
        room = budget - len(lines[peak]) - before - after
        can_left = first > floor and len(lines[first - 1]) + 1 <= room
        can_right = last + 1 < ceiling and len(lines[last + 1]) + 1 <= room
        if not can_left and not can_right:
            break
        if can_left and (not can_right or before <= after):
            first -= 1
            before += len(lines[first]) + 1
        else:
            last += 1
            after += len(lines[last]) + 1
    result = {"lines": [first + 1, last + 1], "page_lines": len(lines),
              "passage": "\n".join(lines[first:last + 1])}
    preceding = [b for b in bookmarks if b.get("line", 0) <= first + 1 and not b.get("unlocated")]
    if preceding:
        result["preceding_section"] = preceding[-1]
    unplaced = [b["title"] for b in bookmarks if b.get("unlocated")]
    if unplaced:
        result["unlocated_page_bookmarks"] = unplaced
    if floor in captions:
        i = floor
        result["preceding_caption"] = {"line": i + 1, "text": lines[i].strip()}
    if floor in lists and floor < first:
        result["preceding_list_intro"] = {"line": floor + 1, "text": lines[floor].strip()}
    return result


def source_pages(root, nvme_files):
    import fitz

    last_heading = ""
    for path in nvme_files:
        page = int(path.stem.split("-")[1])
        headings, body = nvme_page(path)
        context = " ".join(dict.fromkeys([last_heading, *headings]))
        if headings:
            last_heading = headings[-1]
        is_index = bool(len(re.findall(r"\.{8,}", body)) > 4)
        yield "nvme", path.relative_to(root).as_posix(), page, context, body, is_index
    with fitz.open(root / PCIE_PDF) as pdf:
        bookmarks = defaultdict(list)
        for _, heading, page in pdf.get_toc():
            bookmarks[page].append(heading)
        last_heading = ""
        for page, source in enumerate(pdf, 1):
            headings = bookmarks[page]
            context = " ".join(dict.fromkeys([last_heading, *headings]))
            if headings:
                last_heading = headings[-1]
            body = source.get_text()
            is_index = last_heading in {"Table of Contents", "Table of Figures", "Table of Tables"}
            yield "pcie", PCIE_PDF, page, context, body, is_index


def build_index(root, nvme_files, target):
    with closing(sqlite3.connect(target)) as db:
        db.execute("CREATE TABLE pages(protocol TEXT, path TEXT, page INTEGER, outline INTEGER, body TEXT, PRIMARY KEY(protocol,page))")
        for protocol in PROTOCOLS:
            db.execute(f"CREATE VIRTUAL TABLE {protocol}_pages USING fts5(body, tokenize='porter unicode61')")
            db.execute(f"CREATE VIRTUAL TABLE {protocol}_parts USING fts5(heading,body,page UNINDEXED,tokenize='porter unicode61')")
        for protocol, path, page, heading, body, is_index in source_pages(root, nvme_files):
            db.execute("INSERT INTO pages VALUES(?,?,?,?,?)", (protocol, path, page, is_index, body))
            db.execute(f"INSERT INTO {protocol}_pages(rowid,body) VALUES(?,?)", (page, body))
            db.executemany(
                f"INSERT INTO {protocol}_parts VALUES(?,?,?)",
                ((heading, part, page) for part in windows(body) if not is_index),
            )
        for protocol in PROTOCOLS:
            for tier in ("pages", "parts"):
                table = f"{protocol}_{tier}"
                db.execute(f"INSERT INTO {table}({table}) VALUES('optimize')")
        db.commit()


def corpus_aliases(root, protocol):
    aliases = dict(GLOSSARY)
    directory = root / ("kb/nvme/concepts" if protocol == "nvme" else "kb/pcie/wiki")
    title_re = re.compile(r'^title:\s*["\']?([\u3400-\u9fff]{2,16})\s*[(（]([A-Za-z][A-Za-z0-9 /.-]{1,60})[）)]', re.M)
    for path in sorted(directory.rglob("*.md")):
        with path.open(encoding="utf-8-sig") as src:
            found = title_re.search(src.read(1200))
            if found:
                aliases.setdefault(found[1], found[2])
    return aliases


def supplemental_terms(root, protocol, db):
    directory = root / ("kb/nvme/concepts" if protocol == "nvme" else "kb/pcie/wiki")
    pair = re.compile(r"([\u3400-\u9fff]{2,20})\s*[(（]\s*([A-Za-z][A-Za-z0-9 /-]{1,50})[,，)）]")
    separators = re.compile(r"的|将|通过|提供|多个|采用|使用|包括|支持|称为|一个|所有|这些|必须|以及|允许|其中|对应|或者")
    translations = defaultdict(Counter)
    for file in sorted(directory.rglob("*.md")):
        for chinese, english in pair.findall(file.read_text(encoding="utf-8-sig")):
            key = separators.split(chinese)[-1]
            if 2 <= len(key) <= 12 and len(english.split()) <= 6:
                translations[key][english.strip().lower()] += 1
    definitions = defaultdict(Counter)
    abbreviation = re.compile(r"((?:[A-Za-z][A-Za-z-]*[ \t]+){1,8})\(([A-Z][A-Z0-9]{2,7})\)")
    for (text,) in db.execute("SELECT body FROM pages WHERE protocol=?", (protocol,)):
        for prefix, abbr in abbreviation.findall(" ".join(text.split())):
            words = prefix.strip().split()
            for start in range(len(words)):
                expansion = words[start:]
                initials = "".join(word[0] for word in expansion if word.lower() not in {"of", "and", "the"}).upper()
                if initials == abbr:
                    definitions[abbr][(" ".join(expansion)).lower()] += 1
                    break
    aliases = {key: values.most_common(1)[0][0] for key, values in translations.items()}
    expansions = {key: values.most_common(1)[0][0] for key, values in definitions.items()}
    reference = {page for (page,) in db.execute("SELECT page FROM pages WHERE protocol=? AND outline=1", (protocol,))}
    for page, heading in db.execute(f"SELECT page, heading FROM {protocol}_parts GROUP BY page"):
        if re.search(r"Terms and Acronyms|Revision History|Documentation Conventions", heading, re.I):
            reference.add(page)
    last_page = db.execute("SELECT max(page) FROM pages WHERE protocol=?", (protocol,)).fetchone()[0]
    return aliases, expansions, reference, last_page


class PageRetriever:
    def __init__(self, repo_root: str | Path, cache_dir: str | Path | None = None):
        self.root = Path(repo_root).resolve()
        files = sorted((self.root / NVME_PAGES).glob("page-*.md"))
        if not files:
            raise FileNotFoundError(self.root / NVME_PAGES)
        digest = hashlib.sha256(b"kb-source-page-index-v1")
        for src in [self.root / PCIE_PDF, *files]:
            digest.update(src.relative_to(self.root).as_posix().encode())
            with src.open("rb") as stream:
                digest.update(hashlib.file_digest(stream, "sha256").digest())
        directory = Path(cache_dir) if cache_dir else self.root / ".kb_index"
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / f"spec-pages-{digest.hexdigest()[:18]}.sqlite"
        if not target.is_file():
            descriptor, name = tempfile.mkstemp(prefix="spec-build-", suffix=".sqlite", dir=directory)
            os.close(descriptor)
            tmp = Path(name)
            try:
                build_index(self.root, files, tmp)
                try:
                    os.replace(tmp, target)
                except PermissionError:
                    if not target.is_file():
                        raise
            finally:
                tmp.unlink(missing_ok=True)
        self.db = sqlite3.connect(target.resolve().as_uri() + "?mode=ro", uri=True)
        self.aliases = {p: corpus_aliases(self.root, p) for p in PROTOCOLS}
        self._supplement = {}
        self._bookmarks = {}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        self.db.close()

    def read_page(self, protocol: str, pdf_page: int) -> str:
        row = self.db.execute("SELECT body FROM pages WHERE protocol=? AND page=?", (protocol, pdf_page)).fetchone()
        if row is None:
            raise KeyError((protocol, pdf_page))
        return row[0]

    def preview(self, protocol: str, pdf_page: int, query: str) -> str:
        if protocol not in PROTOCOLS:
            raise ValueError("Unknown protocol")
        table = f"{protocol}_parts"
        expr = query_expression(query, self.aliases[protocol], True)
        if expr:
            best = self.db.execute(
                f"SELECT body FROM {table} WHERE {table} MATCH ? AND page=? "
                f"ORDER BY bm25({table}, 0.0, 1.0), rowid LIMIT 1",
                (expr, pdf_page),
            ).fetchone()
            if best:
                return best[0]
        return next(windows(self.read_page(protocol, pdf_page)), "")

    def page_bookmarks(self, protocol, pdf_page, body):
        if protocol not in self._bookmarks:
            by_page = defaultdict(list)
            if protocol == "nvme":
                for path in sorted((self.root / NVME_PAGES).glob("page-*.md")):
                    titles, _ = nvme_page(path)
                    if titles:
                        by_page[int(path.stem.split("-")[1])] = titles
            elif protocol == "pcie":
                import fitz

                with fitz.open(self.root / PCIE_PDF) as source:
                    for _, title, page in source.get_toc():
                        by_page[page].append(title)
            else:
                raise ValueError("Unknown protocol")
            self._bookmarks[protocol] = by_page
        by_page = self._bookmarks[protocol]
        prior = max((p for p in by_page if 0 < p < pdf_page), default=None)
        entries = [{"title": by_page[prior][-1], "pdf_page": prior}] if prior else []
        lines = body.splitlines()
        start = 0
        for title in by_page.get(pdf_page, ()):
            entry = {"title": title, "pdf_page": pdf_page}
            line = heading_line(lines, title, start)
            if line is None:
                entry["unlocated"] = True
            else:
                entry["line"] = line
                start = line
            entries.append(entry)
        return entries

    def scoped_passage(self, protocol: str, pdf_page: int, query: str) -> dict:
        preview = self.preview(protocol, pdf_page, query)
        body = self.read_page(protocol, pdf_page)
        result = locate_passage(body, preview, query_expression(query, self.aliases[protocol], True),
                                self.page_bookmarks(protocol, pdf_page, body))
        if result["lines"]:
            first, last = result["lines"]
            candidates = []
            if first == 1:
                candidates.append(pdf_page - 1)
            if last == result["page_lines"]:
                candidates.append(pdf_page + 1)
            neighbors = [page for page in candidates if self.db.execute(
                "SELECT 1 FROM pages WHERE protocol=? AND page=?", (protocol, page)).fetchone()]
            if neighbors:
                result["adjacent_pages_at_excerpt_edge"] = neighbors
        return result

    def outcome_passage(self, protocol: str, pdf_page: int, query: str) -> dict:
        excerpt = self.scoped_passage(protocol, pdf_page, query)
        excerpt["value_table"] = None
        excerpt["outcome_scope"] = "recognized layouts on this PDF page only"
        if not excerpt["lines"]:
            return excerpt
        body = self.read_page(protocol, pdf_page)
        lines = body.splitlines()
        index = page_outcomes(body, self.page_bookmarks(protocol, pdf_page, body))
        first, last = excerpt["lines"]
        terms = set(WORD.findall(query.casefold()))
        groups = [g for g in index["value_tables"] if g["field_line"] <= last and g["rows"][-1][2] >= first]
        if groups:
            def priority(group):
                field = set(WORD.findall(group["field"].casefold()))
                overlap = min(last, group["rows"][-1][2]) - max(first, group["field_line"]) + 1
                return len(terms & field), overlap

            group = max(groups, key=priority)
            excerpt["value_table"] = group
            start, end = group["field_line"], group["rows"][-1][2]
            if len("\n".join(lines[start - 1:end])) <= 2300:
                first, last = start, end
                excerpt["lines"] = [first, last]
                excerpt["passage"] = "\n".join(lines[first - 1:last])
        applicable = [span for span in index["condition_lines"] if span[0] <= last and span[1] >= first]
        if applicable:
            if not groups:
                boundaries = {b["line"] for b in self.page_bookmarks(protocol, pdf_page, body) if b.get("line")}
                boundaries.update(i for i, line in enumerate(lines, 1) if CAPTION.match(line))
                floor = max((n for n in boundaries if n <= first), default=1)
                ceiling = min((n for n in boundaries if n > last), default=len(lines) + 1)
                adjacent = [span for span in index["condition_lines"] if floor <= span[0] < ceiling
                            and span[0] <= last + 2 and span[1] >= first - 2]
                if adjacent and len("\n".join(lines[min(first, adjacent[0][0]) - 1:max(last, adjacent[-1][1])])) <= 2300:
                    applicable = adjacent
            excerpt["condition_lines"] = applicable
            first, last = min(first, applicable[0][0]), max(last, applicable[-1][1])
            if len("\n".join(lines[first - 1:last])) <= 2300:
                excerpt["lines"] = [first, last]
                excerpt["passage"] = "\n".join(lines[first - 1:last])
        return excerpt

    def search(self, protocol: str, query: str, mode: str = "domain", k: int = 5) -> list[dict]:
        if protocol not in PROTOCOLS or mode not in MODES or not 1 <= k <= 100:
            raise ValueError("Unknown protocol, unknown mode, or k outside 1..100")
        if mode == "refined":
            return self._refined(protocol, query, k)
        if mode == "fusion":
            scores = defaultdict(float)
            for component in ("expanded", "domain"):
                hits = self.search(protocol, query, component, max(k, 20))
                for rank, hit in enumerate(hits, 1):
                    scores[hit["pdf_page"]] += 1 / (20 + rank)
            ordered = sorted(scores, key=lambda page: (-scores[page], page))
            return [self._hit(protocol, page) for page in ordered[:k]]
        expr = query_expression(query, self.aliases[protocol], mode != "bm25")
        if not expr:
            return []
        if mode == "domain":
            table = f"{protocol}_parts"
            sql = f"""
                WITH passages AS MATERIALIZED (
                    SELECT page, bm25({table}, 1.6, 1.0) AS score
                    FROM {table} WHERE {table} MATCH ? ORDER BY score LIMIT ?
                )
                SELECT page, min(score) AS best FROM passages
                GROUP BY page ORDER BY best, page LIMIT ?
            """
            ranking = self.db.execute(sql, (expr, max(200, k * 20), k))
        else:
            table = f"{protocol}_pages"
            sql = f"SELECT rowid, rank FROM {table} WHERE {table} MATCH ? ORDER BY rank, rowid LIMIT ?"
            ranking = self.db.execute(sql, (expr, k))
        return [self._hit(protocol, page) for page, _ in ranking]

    def _refined(self, protocol, query, k):
        if protocol not in self._supplement:
            self._supplement[protocol] = supplemental_terms(self.root, protocol, self.db)
        aliases, acronyms, reference, last_page = self._supplement[protocol]
        extra = [english for chinese, english in aliases.items() if chinese in query and self.aliases[protocol].get(chinese, "").lower() != english]
        extra.extend(acronyms[word] for word in WORD.findall(query) if word in acronyms)
        augmented = " | ".join([query, *dict.fromkeys(extra)])
        scores = defaultdict(float)
        components = (("domain", query, 1), ("expanded", query, 1),
                      ("domain", augmented, .4), ("expanded", augmented, .4), ("bm25", query, .4))
        combined = defaultdict(float)
        for mode, text, weight in components:
            combined[mode, text] += weight
        for (mode, text), weight in combined.items():
            for rank, hit in enumerate(self.search(protocol, text, mode, max(30, k)), 1):
                scores[hit["pdf_page"]] += weight / (20 + rank)
        candidates = {neighbor for page in scores for neighbor in (page - 1, page, page + 1) if 1 <= neighbor <= last_page}
        def strength(page):
            central = scores.get(page, 0) + 0.08 * (scores.get(page - 1, 0) + scores.get(page + 1, 0))
            return central * (0.65 if page in reference else 1)
        ordered = sorted(candidates, key=lambda page: (-strength(page), page))
        return [self._hit(protocol, page) for page in ordered[:k]]

    def _hit(self, protocol, page):
        path = PCIE_PDF if protocol == "pcie" else f"{NVME_PAGES}/page-{page:03d}.md"
        return {"path": path, "pdf_page": page}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol", choices=PROTOCOLS)
    parser.add_argument("query")
    parser.add_argument("--mode", choices=MODES, default="domain")
    parser.add_argument("-k", type=int, default=5)
    from benchmark import ROOT

    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    with PageRetriever(args.root) as retriever:
        print(json.dumps(retriever.search(args.protocol, args.query, args.mode, args.k), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
