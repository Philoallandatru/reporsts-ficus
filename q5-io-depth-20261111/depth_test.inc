static void test_depth_eight(llama_expert_store & index, ggml_tensor * t, const std::vector<uint8_t> & reference) {
    const size_t budget = 3*1024*1024;
    for (bool fail_upload : {false, true}) {
        llama_expert_session session(index, nullptr, {budget, 1024*1024, 8});
        auto read_all = [&](delayed_consumer & sink) {
            bool sent = false;
            session.transfer([&](llama_expert_session::request & req) {
                if (sent) {
                    return false;
                }
                sent = true;
                req = {t, nullptr, 0, 0, ggml_nbytes(t)};
                return true;
            }, sink);
        };
        unsigned reads = 0;
        session.test_observer = [&](llama_expert_session::test_event event, const llama_expert_session::stats &) {
            if (!fail_upload && event == llama_expert_session::test_event::read_submitted && ++reads == 8) {
                throw llama_expert_store_cancelled();
            }
            if (fail_upload && event == llama_expert_session::test_event::upload_submitted) {
                throw std::runtime_error("injected upload failure");
            }
        };
        delayed_consumer failed(reference, 37);
        rejects([&] { read_all(failed); });
        const auto cancelled = session.snapshot();
        require(cancelled.peak_in_flight == 8, "fixture did not fill all eight slots");
        require(cancelled.reads_drained == (fail_upload ? 7 : 8), "pending reads not drained");
        require(cancelled.uploads_drained == (fail_upload ? 1 : 0), "pending upload not drained");
        require(cancelled.ram_live == 0 && failed.pending == 0 && failed.correct, "incomplete entry or stale data after failure");
        require_idle(session, budget, 8);
        session.test_observer = {};
        delayed_consumer retried(reference, 37);
        read_all(retried);
        require(retried.correct && retried.checked == ggml_nbytes(t) && retried.pending == 0, "eight-slot retry corrupted data");
        require_idle(session, budget, 8);
        const auto retried_reads = session.snapshot().reads;
        compare(session, t, 0, ggml_nbytes(t), reference, 37);
        require(session.snapshot().reads == retried_reads, "completed cache fill was not retained");
    }
    printf("eight slots, cancellation, upload drain, retry and cache hit PASSED\n");
}

