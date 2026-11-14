#define NOMINMAX
#include <windows.h>

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

static constexpr size_t slot_count = 8;
static constexpr size_t slot_bytes = 4*1024*1024;
static constexpr size_t request_count = 1536;
using clock_type = std::chrono::steady_clock;

struct handle {
    HANDLE value = nullptr;
    ~handle() { if (value && value != INVALID_HANDLE_VALUE) CloseHandle(value); }
};

struct read_slot {
    handle event;
    OVERLAPPED ov = {};
    DWORD bytes = 0;
    bool busy = false;
};

static void check(bool ok, const char * what) {
    if (!ok) throw std::runtime_error(std::string(what) + ": " + std::to_string(GetLastError()));
}

int wmain(int argc, wchar_t ** argv) {
    if (argc != 3 || (argv[2][0] != L'0' && argv[2][0] != L'1')) return 2;
    const bool mapped = argv[2][0] == L'1';
    handle normal, map, direct;
    void * view = nullptr;
    void * memory = nullptr;
    std::array<read_slot,slot_count> slots;
    int code = 0;
    try {
        normal.value = CreateFileW(argv[1], GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
        check(normal.value != INVALID_HANDLE_VALUE, "open normal handle");
        if (mapped) {
            map.value = CreateFileMappingW(normal.value, nullptr, PAGE_READONLY, 0, 0, nullptr);
            check(map.value != nullptr, "create read-only mapping");
            view = MapViewOfFile(map.value, FILE_MAP_READ, 0, 0, 0);
            check(view != nullptr, "map view");
        }
        direct.value = CreateFileW(argv[1], GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING,
                                   FILE_FLAG_NO_BUFFERING | FILE_FLAG_OVERLAPPED | FILE_FLAG_RANDOM_ACCESS, nullptr);
        check(direct.value != INVALID_HANDLE_VALUE, "open direct handle");
        FILE_STORAGE_INFO storage = {};
        check(GetFileInformationByHandleEx(direct.value, FileStorageInfo, &storage, sizeof(storage)) != 0, "file sector alignment");
        const DWORD alignment = std::max({storage.LogicalBytesPerSector, storage.PhysicalBytesPerSectorForPerformance,
                                          storage.PhysicalBytesPerSectorForAtomicity});
        check(alignment && (1104*1024)%alignment == 0 && (1704*1024)%alignment == 0 && slot_bytes%alignment == 0, "request alignment");
        LARGE_INTEGER size = {};
        check(GetFileSizeEx(direct.value, &size) != 0, "file size");
        const size_t extent_count = size.QuadPart > 0 ? static_cast<size_t>(size.QuadPart)/slot_bytes : 0;
        check(extent_count >= request_count + 32, "shard too small");
        std::vector<size_t> extents(extent_count - 32);
        std::iota(extents.begin(), extents.end(), size_t(32));
        std::shuffle(extents.begin(), extents.end(), std::mt19937(6416));
        memory = VirtualAlloc(nullptr, slot_count*slot_bytes, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
        check(memory != nullptr && reinterpret_cast<uintptr_t>(memory)%alignment == 0, "allocate staging");
        for (auto & slot : slots) {
            slot.event.value = CreateEventW(nullptr, TRUE, FALSE, nullptr);
            check(slot.event.value != nullptr, "create event");
        }
        uint64_t bytes_read = 0, pending = 0;
        double submit_ms = 0;
        std::vector<double> submits;
        submits.reserve(request_count);
        auto finish = [&](read_slot & slot) {
            DWORD got = 0;
            check(GetOverlappedResult(direct.value, &slot.ov, &got, TRUE) != 0, "complete direct read");
            slot.busy = false;
            check(got == slot.bytes, "short direct read");
            bytes_read += got;
        };
        const auto start = clock_type::now();
        for (size_t i = 0; i < request_count; ++i) {
            auto & slot = slots[i % slot_count];
            if (slot.busy) finish(slot);
            const uint64_t offset = uint64_t(extents[i])*slot_bytes;
            slot.ov = {};
            slot.ov.Offset = DWORD(offset);
            slot.ov.OffsetHigh = DWORD(offset >> 32);
            slot.ov.hEvent = slot.event.value;
            ResetEvent(slot.event.value);
            slot.bytes = (i%3 == 0 ? 1704 : 1104)*1024;
            const auto before = clock_type::now();
            const BOOL ok = ReadFile(direct.value, static_cast<char *>(memory)+(i%slot_count)*slot_bytes, slot.bytes, nullptr, &slot.ov);
            const DWORD error = ok ? ERROR_SUCCESS : GetLastError();
            const double dt = std::chrono::duration<double,std::milli>(clock_type::now()-before).count();
            if (!ok && error != ERROR_IO_PENDING) throw std::runtime_error("submit direct read: " + std::to_string(error));
            pending += !ok;
            slot.busy = true;
            submit_ms += dt;
            submits.push_back(dt);
        }
        for (auto & slot : slots) if (slot.busy) finish(slot);
        const double elapsed = std::chrono::duration<double>(clock_type::now()-start).count();
        std::sort(submits.begin(),submits.end());
        std::cout << std::setprecision(10) << "{\"pid\":" << GetCurrentProcessId() << ",\"mapped\":" << mapped
                  << ",\"requests\":" << request_count << ",\"bytes\":" << bytes_read << ",\"pending\":" << pending
                  << ",\"elapsed_s\":" << elapsed << ",\"submit_total_ms\":" << submit_ms
                  << ",\"submit_p50_ms\":" << submits[request_count/2] << ",\"submit_p95_ms\":" << submits[request_count*95/100] << "}\n";
    } catch (const std::exception & e) {
        std::cerr << e.what() << '\n';
        for (auto & slot : slots) if (slot.busy) CancelIoEx(direct.value,&slot.ov);
        for (auto & slot : slots) if (slot.busy) { DWORD got; GetOverlappedResult(direct.value,&slot.ov,&got,TRUE); }
        code = 1;
    }
    if (memory) VirtualFree(memory,0,MEM_RELEASE);
    if (view) UnmapViewOfFile(view);
    return code;
}
