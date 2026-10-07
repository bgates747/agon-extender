cmake_minimum_required(VERSION 3.16)
set(EXTRA_COMPONENT_DIRS
    "${CMAKE_CURRENT_LIST_DIR}/components/esp-bsp/bsp/esp32_p4_function_ev_board"
    "${CMAKE_CURRENT_LIST_DIR}/components")
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(p4pc_playground)
