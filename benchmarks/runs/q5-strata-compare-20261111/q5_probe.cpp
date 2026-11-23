#include "llama.h"
#include "llama-ext.h"
#include "ggml-backend.h"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <vector>

using clock_type = std::chrono::steady_clock;

static double ms(clock_type::time_point a, clock_type::time_point b) {
    return std::chrono::duration<double, std::milli>(b - a).count();
}

int main(int argc, char ** argv) {
    if (argc != 2) return 2;
    ggml_backend_load_all();
    llama_backend_init();
    try {
        auto mp = llama_model_default_params();
        mp.load_mode = LLAMA_LOAD_MODE_MMAP;
        mp.use_extra_bufts = false;
        const auto gpu = ggml_backend_dev_by_name("CUDA0");
        const auto cpu = ggml_backend_dev_by_type(GGML_BACKEND_DEVICE_TYPE_CPU);
        if (!gpu || !cpu) throw std::runtime_error("CUDA0 and CPU required");
        ggml_backend_dev_t devices[] = {gpu, nullptr};
        llama_model_tensor_buft_override overrides[] = {
            {"\\.ffn_(gate|up|down|gate_up)_exps\\.weight$", ggml_backend_dev_buffer_type(cpu)}, {nullptr, nullptr}};
        mp.devices = devices;
        mp.split_mode = LLAMA_SPLIT_MODE_NONE;
        mp.n_gpu_layers = 999;
        mp.tensor_buft_overrides = overrides;
        std::unique_ptr<llama_model, decltype(&llama_model_free)> model(llama_model_load_from_file(argv[1], mp), llama_model_free);
        if (!model) throw std::runtime_error("model load failed");
        const auto vocab = llama_model_get_vocab(model.get());
        auto cp = llama_context_default_params();
        cp.n_ctx = 32768;
        cp.n_batch = cp.n_ubatch = 512;
        cp.n_seq_max = 1;
        cp.n_threads = cp.n_threads_batch = 16;
        cp.moe_cache_size = 4096 * size_t(1048576);
        cp.moe_cache_cpu_share = 0;
        cp.type_k = cp.type_v = GGML_TYPE_Q8_0;
        cp.flash_attn_type = LLAMA_FLASH_ATTN_TYPE_ENABLED;
        std::unique_ptr<llama_context, decltype(&llama_free)> ctx(llama_init_from_model(model.get(), cp), llama_free);
        if (!ctx) throw std::runtime_error("context creation failed");
        for (const auto & e : llama_get_memory_breakdown(ctx.get())) {
            std::cout << "MEM " << ggml_backend_buft_name(e.first) << ' ' << e.second.model << ' '
                      << e.second.context << ' ' << e.second.compute << '\n';
        }
        std::cout << "UBATCH " << llama_n_ubatch(ctx.get()) << '\n';
        std::cout << "READY " << llama_n_ctx(ctx.get()) << std::endl;
        std::string line;
        if (!std::getline(std::cin, line)) return 2;
        std::istringstream request(line);
        std::string op, csv, continuation;
        int count = 0;
        request >> op >> count >> csv >> continuation;
        if (op != "GEN" || count != 128) throw std::runtime_error("bad request");
        const int nv = llama_vocab_n_tokens(vocab);
        auto parse = [&](const std::string & text) {
            std::istringstream ids(text);
            std::string field;
            std::vector<llama_token> tokens;
            while (std::getline(ids, field, ',')) {
                int token = std::stoi(field);
                if (token < 0 || token >= nv) throw std::runtime_error("bad token");
                tokens.push_back(token);
            }
            return tokens;
        };
        const auto prompt = parse(csv);
        const auto forced = parse(continuation);
        if (prompt.size() != 128 || forced.size() != (size_t) count) throw std::runtime_error("bad trajectory length");
        auto decode = [&](const llama_token * input, int n) {
            llama_batch batch = llama_batch_get_one(const_cast<llama_token *>(input), n);
            if (llama_decode(ctx.get(), batch) != 0) throw std::runtime_error("decode failed");
            llama_synchronize(ctx.get());
        };
        const auto start = clock_type::now();
        decode(prompt.data(), (int) prompt.size());
        const auto prefilled = clock_type::now();
        auto first = prefilled;
        auto last = first;
        int matched = 0;
        for (int i = 0; i < count; ++i) {
            const auto logits = llama_get_logits_ith(ctx.get(), -1);
            if (!logits || !std::all_of(logits, logits + nv, [](float v) { return std::isfinite(v); })) {
                throw std::runtime_error("invalid logits");
            }
            const auto token = forced[i];
            matched += token == (llama_token) (std::max_element(logits, logits + nv) - logits);
            last = clock_type::now();
            if (!i) first = last;
            std::cout << "T " << token << std::endl;
            if (i + 1 < count) decode(&token, 1);
        }
        std::cout << "DONE " << count << ' ' << prompt.size() << ' ' << ms(start, prefilled) << ' '
                  << ms(first, last) << " length 0 0 0" << std::endl;
        std::cout << "GREEDY_MATCH " << matched << std::endl;
        llama_perf_context_print(ctx.get());
        std::getline(std::cin, line);
        ctx.reset();
        model.reset();
        llama_backend_free();
        return 0;
    } catch (const std::exception & e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }
}
