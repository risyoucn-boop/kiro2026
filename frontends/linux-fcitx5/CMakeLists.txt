cmake_minimum_required(VERSION 3.16)
project(synapse-fcitx5
    VERSION 0.0.1
    LANGUAGES CXX
    DESCRIPTION "Synapse Nexus — Fcitx5 input method engine")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE RelWithDebInfo CACHE STRING "" FORCE)
endif()

# Required Fcitx5 packages.
find_package(ECM 1.0.0 REQUIRED)
list(APPEND CMAKE_MODULE_PATH ${ECM_MODULE_PATH})
find_package(Fcitx5Core REQUIRED)
find_package(Fcitx5Utils REQUIRED)
find_package(Fcitx5Module REQUIRED COMPONENTS InputContext)

include(GNUInstallDirs)

add_library(synapse MODULE
    src/synapse_engine.cpp
    src/synapse_factory.cpp
)
target_include_directories(synapse PRIVATE src)
target_link_libraries(synapse
    PRIVATE
        Fcitx5::Core
        Fcitx5::Utils
)

# Fcitx5 expects the addon shared library, addon metadata file and
# input-method registration file in well-known directories.
set(FCITX5_ADDON_LIB_DIR  "${CMAKE_INSTALL_LIBDIR}/fcitx5")
set(FCITX5_ADDON_CONF_DIR "${CMAKE_INSTALL_DATADIR}/fcitx5/addon")
set(FCITX5_INPUTMETHOD_DIR "${CMAKE_INSTALL_DATADIR}/fcitx5/inputmethod")

install(TARGETS synapse DESTINATION ${FCITX5_ADDON_LIB_DIR})

configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/data/synapse-addon.conf.in"
    "${CMAKE_CURRENT_BINARY_DIR}/synapse.conf"
    @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/synapse.conf"
        DESTINATION ${FCITX5_ADDON_CONF_DIR})

install(FILES data/synapse.conf-im
        RENAME synapse.conf
        DESTINATION ${FCITX5_INPUTMETHOD_DIR})

message(STATUS "synapse-fcitx5 will install:")
message(STATUS "  addon lib  -> ${CMAKE_INSTALL_PREFIX}/${FCITX5_ADDON_LIB_DIR}")
message(STATUS "  addon conf -> ${CMAKE_INSTALL_PREFIX}/${FCITX5_ADDON_CONF_DIR}")
message(STATUS "  im   conf  -> ${CMAKE_INSTALL_PREFIX}/${FCITX5_INPUTMETHOD_DIR}")
