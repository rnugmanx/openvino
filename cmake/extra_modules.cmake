# Copyright (C) 2018-2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

function(ie_generate_dev_package_config)
    # dummy check that OpenCV is here
    find_package(OpenCV QUIET)

    foreach(component IN LISTS openvino_export_components)
        # export all targets with prefix and use them during extra modules build
        export(TARGETS ${${component}} NAMESPACE IE::
               APPEND FILE "${CMAKE_BINARY_DIR}/${component}_dev_targets.cmake")
        list(APPEND all_dev_targets ${${component}})
    endforeach()
    add_custom_target(ie_dev_targets DEPENDS ${all_dev_targets})

    # if we've found system gflags
    if(gflags_DIR)
        set(gflags_BINARY_DIR "${gflags_DIR}")
    endif()

    configure_package_config_file("${OpenVINO_SOURCE_DIR}/cmake/templates/InferenceEngineDeveloperPackageConfig.cmake.in"
                                  "${CMAKE_BINARY_DIR}/InferenceEngineDeveloperPackageConfig.cmake"
                                  INSTALL_DESTINATION share # not used
                                  PATH_VARS "OpenVINO_SOURCE_DIR;gflags_BINARY_DIR"
                                  NO_CHECK_REQUIRED_COMPONENTS_MACRO)

    configure_file("${OpenVINO_SOURCE_DIR}/cmake/templates/InferenceEngineConfig-version.cmake.in"
                   "${CMAKE_BINARY_DIR}/InferenceEngineDeveloperPackageConfig-version.cmake"
                   @ONLY)
endfunction()

function(ov_generate_dev_package_config)
    # dummy check that OpenCV is here
    find_package(OpenCV QUIET)

    foreach(component IN LISTS openvino_export_components)
        # TODO: remove legacy targets from tests
        # string(FIND "${component}" "_legacy" index)
        # if(index EQUAL -1)

        # export all targets with prefix and use them during extra modules build
        export(TARGETS ${${component}} NAMESPACE openvino::
               APPEND FILE "${CMAKE_BINARY_DIR}/ov_${component}_dev_targets.cmake")
        list(APPEND all_dev_targets ${${component}})
        # endif()
    endforeach()
    add_custom_target(ov_dev_targets DEPENDS ${all_dev_targets})

    # if we've found system gflags
    if(gflags_DIR)
        set(gflags_BINARY_DIR "${gflags_DIR}")
    endif()

    configure_package_config_file("${OpenVINO_SOURCE_DIR}/cmake/templates/OpenVINODeveloperPackageConfig.cmake.in"
                                  "${CMAKE_BINARY_DIR}/OpenVINODeveloperPackageConfig.cmake"
                                  INSTALL_DESTINATION share # not used
                                  PATH_VARS "OpenVINO_SOURCE_DIR;gflags_BINARY_DIR"
                                  NO_CHECK_REQUIRED_COMPONENTS_MACRO)

    configure_file("${OpenVINO_SOURCE_DIR}/cmake/templates/OpenVINOConfig-version.cmake.in"
                   "${CMAKE_BINARY_DIR}/OpenVINODeveloperPackageConfig-version.cmake" 
                   @ONLY)
endfunction()

#
# Add extra modules
#

function(register_extra_modules)
    # post export
    openvino_developer_export_targets(COMPONENT core_legacy TARGETS inference_engine)
    openvino_developer_export_targets(COMPONENT core_legacy TARGETS ngraph)

    set(InferenceEngineDeveloperPackage_DIR "${CMAKE_CURRENT_BINARY_DIR}/runtime")
    set(OpenVINODeveloperPackage_DIR "${CMAKE_BINARY_DIR}/runtime")
    set(OpenVINO_DIR ${CMAKE_BINARY_DIR})


    function(generate_fake_dev_package NS)
        if(NS STREQUAL "openvino")
            set(devconfig_file "${OpenVINODeveloperPackage_DIR}/OpenVINODeveloperPackageConfig.cmake")
        else()
            set(devconfig_file "${InferenceEngineDeveloperPackage_DIR}/InferenceEngineDeveloperPackageConfig.cmake")
        endif()
        file(REMOVE "${devconfig_file}")

        file(WRITE "${devconfig_file}" "\# !! AUTOGENERATED: DON'T EDIT !!\n\n")
        file(APPEND "${devconfig_file}" "ie_deprecated_no_errors()\n")

        foreach(target IN LISTS ${openvino_export_components})
            if(target)
                file(APPEND "${devconfig_file}" "add_library(${NS}::${target} ALIAS ${target})\n")
            endif()
        endforeach()
    endfunction()

    generate_fake_dev_package("openvino")
    generate_fake_dev_package("IE")

    # detect where IE_EXTRA_MODULES contains folders with CMakeLists.txt
    # other folders are supposed to have sub-folders with CMakeLists.txt
    foreach(module_path IN LISTS IE_EXTRA_MODULES)
        get_filename_component(module_path "${module_path}" ABSOLUTE)
        if(EXISTS "${module_path}/CMakeLists.txt")
            list(APPEND extra_modules "${module_path}")
        elseif(module_path)
            file(GLOB extra_modules ${extra_modules} "${module_path}/*")
        endif()
    endforeach()

    # add template plugin
    if(ENABLE_TEMPLATE)
        list(APPEND extra_modules "${OpenVINO_SOURCE_DIR}/src/plugins/template")
    endif()
    list(APPEND extra_modules "${OpenVINO_SOURCE_DIR}/src/core/template_extension")

    # add each extra module
    foreach(module_path IN LISTS extra_modules)
        if(module_path)
            get_filename_component(module_name "${module_path}" NAME)
            set(build_module ON)
            if(NOT EXISTS "${module_path}/CMakeLists.txt") # if module is built not using cmake
                set(build_module OFF)
            endif()
            if(NOT DEFINED BUILD_${module_name})
                set(BUILD_${module_name} ${build_module} CACHE BOOL "Build ${module_name} extra module" FORCE)
            endif()
            if(BUILD_${module_name})
                message(STATUS "Register ${module_name} to be built in build-modules/${module_name}")
                add_subdirectory("${module_path}" "build-modules/${module_name}")
            endif()
        endif()
    endforeach()
endfunction()

#
# Extra modules support
#

# this InferenceEngineDeveloperPackageConfig.cmake is not used
# during extra modules build since it's generated after modules
# are configured
ie_generate_dev_package_config()
ov_generate_dev_package_config()

# extra modules must be registered after inference_engine library
# and all other OpenVINO Core libraries are creared
# because 'register_extra_modules' creates fake InferenceEngineDeveloperPackageConfig.cmake
# with all imported developer targets
register_extra_modules()

# for static libraries case we need to generate final ie_plugins.hpp
# with all the information about plugins
ie_generate_plugins_hpp()

# used for static build
ov_generate_frontends_hpp()
