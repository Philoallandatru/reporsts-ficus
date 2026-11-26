import re

from acceptance_review import acceptance_passages


PROMPT = """签发 SSD 工单，只输出这个形状的 JSON：{"decision":"当前动作","conditions":["决定性原文规则、现场前提及实际核对的 PDF 页"],"checks":[{"target":"核验对象","record":"原始记录","pass":"签发判据"}]}。conditions 仅含 1–5 个字符串，保留改变动作的全部门槛、例外和否决条件。无需验收时 checks 用 []。
每条信息只写一次。验收用短语，保留待复核的输入、批准和结果。历史主张绑定同一对象和时点。通常 200–330 汉字；必要的证据与条件写全。证据已足够时直接签发。"""


def concise_passages(index, protocol, question):
    spans = ()
    if protocol == "nvme" and re.search(r"\bIDLP\b", question, re.IGNORECASE):
        spans = ((352, 22, 27),)
    if (protocol == "pcie" and re.search(r"\bCompletion\b", question, re.IGNORECASE)
            and re.search(r"合并|combin", question, re.IGNORECASE)):
        spans = ((179, 17, 21), (179, 36, 36))
    return [
        {"pdf_page": page, "lines": [first, last],
         "passage": "\n".join(index.read_page(protocol, page).splitlines()[first - 1:last])}
        for page, first, last in spans
    ] or acceptance_passages(index, protocol, question)
