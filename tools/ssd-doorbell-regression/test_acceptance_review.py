import json
import unittest

from acceptance_review import acceptance_passages, format_acceptance
from benchmark import ROOT
from field_evidence import field_passages
from retrieval_trial import PageRetriever


class AcceptanceReviewTest(unittest.TestCase):
    def test_renders_target_record_and_pass_and_handles_a_short_model_preamble(self):
        reply = {"decision": "待验", "conditions": ["表项已掩蔽"], "checks": [
            {"target": "解掩后的实际消息", "record": "同一表项的 DWORD Memory Write", "pass": "地址和数据均匹配"}]}
        raw = "先核对记录。\n```json\n" + json.dumps(reply, ensure_ascii=False) + "\n```"
        self.assertIn("**解掩后的实际消息**。记录为同一表项的 DWORD Memory Write。通过条件为地址和数据均匹配。",
                      format_acceptance(raw))

    def test_rejects_missing_pass_criteria_or_multiple_documents(self):
        reply = {"decision": "待验", "conditions": ["表项已掩蔽"], "checks": [
            {"target": "消息", "record": "抓包", "pass": " "}]}
        self.assertEqual(format_acceptance(json.dumps(reply)), "")
        self.assertEqual(format_acceptance(json.dumps({**reply, "checks": []}) + "\n{}"), "")
        self.assertEqual(format_acceptance("[" + json.dumps(reply) + "]"), "")

    def test_msix_address_data_prefetch_preserves_send_and_cache_rules(self):
        with PageRetriever(ROOT) as index:
            passages = acceptance_passages(index, "pcie", "MSI-X Message Address/Data 改写验收")
        self.assertTrue(any(e["pdf_page"] == 500 and "DWORD Memory Write" in e["passage"] for e in passages))
        self.assertTrue(any(e["pdf_page"] == 501 and "must update" in e["passage"] for e in passages))

    def test_prefetch_contains_scale_and_window_alongside_other_active_rules(self):
        with PageRetriever(ROOT) as index:
            passages = field_passages(index, "nvme", "核对 IPS / IDLP、DNR 和 Flush")
        pages = {entry["pdf_page"]: entry["passage"] for entry in passages}
        self.assertIn("10b 0.01 W", pages[352])
        self.assertIn("idle for 10 seconds", pages[352])
        self.assertIn("command is expected to fail", pages[162])
        self.assertIn("completed by the controller prior to the submission", pages[485])

    def test_slot_acceptance_keeps_configuration_pages_when_eventidx_is_a_witness(self):
        question = ("控制器重启后沿用原物理页。本次工单要签最高合法 SQ Tail/CQ Head 的实际快速路径恢复，能验收吗？\n\n"
                    "现场观测\n- 新 Doorbell Buffer Config 的有效 CQE 成功，同次轨迹有 PRP1 Shadow 和 PRP2 EventIdx 槽写。")
        with PageRetriever(ROOT) as index:
            passages = field_passages(index, "nvme", question)
        self.assertEqual({entry["pdf_page"] for entry in passages}, {445, 446})

    def test_notification_acceptance_keeps_the_eventidx_rule_even_when_slots_are_verified(self):
        question = ("最高合法 SQ Tail 槽位已核，Shadow 从 4 推到 7，未写控制器门铃可以签通知符合吗？\n\n"
                    "现场观测\n- 同次 EventIdx=9。")
        with PageRetriever(ROOT) as index:
            passages = field_passages(index, "nvme", question)
        self.assertIn(702, {entry["pdf_page"] for entry in passages})
