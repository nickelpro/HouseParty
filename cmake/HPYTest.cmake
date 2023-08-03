include_guard()

find_package(nyu-cmake CONFIG REQUIRED)
find_program(FIRTOOL firtool REQUIRED)

set(HPY_PROG ${CMAKE_SOURCE_DIR}/hpy)

function(nyu_add_hpy TARGET)
  foreach(src IN LISTS ARGN)
    cmake_path(ABSOLUTE_PATH src OUTPUT_VARIABLE src_in)
    cmake_path(RELATIVE_PATH src_in BASE_DIRECTORY ${CMAKE_SOURCE_DIR} OUTPUT_VARIABLE out_var)
    cmake_path(ABSOLUTE_PATH out_var BASE_DIRECTORY ${CMAKE_BINARY_DIR})
    cmake_path(REPLACE_EXTENSION out_var v)
    execute_process(
      COMMAND ${HPY_PROG} ${src_in}
      COMMAND ${FIRTOOL} -format=mlir --strip-debug-info
      OUTPUT_FILE ${out_var}
      COMMAND_ERROR_IS_FATAL ANY
    )
    nyu_add_sv(${TARGET} ${out_var})
  endforeach()
endfunction()
