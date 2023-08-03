find_package(Catch2 3 REQUIRED CONFIG)
find_package(nyu-util REQUIRED CONFIG)

add_executable(tests)
target_sources(tests PRIVATE
  DFlipFlop.cpp
)
nyu_link_sv(tests PRIVATE testLib)
nyu_target_verilate(tests
  TOP_MODULES DFlipFlop
  ARGS TRACE_FST
  PREFIX HPDFlipFlop
  VERILATOR_ARGS -Wno-UNOPTFLAT
)
target_link_libraries(tests PRIVATE
  Catch2::Catch2WithMain nyu::testutil
)
target_compile_features(tests PRIVATE cxx_std_23)

include(Catch)
catch_discover_tests(tests)
