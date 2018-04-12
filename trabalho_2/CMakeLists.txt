cmake_minimum_required(VERSION 2.8)
project(Picking)

set(CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS} -std=c++11)

file(GLOB_RECURSE SOURCE_FILES
	"src/*.hpp"
	"src/*.h"
	"src/*.cpp"
	"src/*.c"
)

add_executable(picking ${SOURCE_FILES})

find_package(PkgConfig REQUIRED)
pkg_search_module(GLFW REQUIRED glfw3)
#pkg_search_module(DL_LIBRARY REQUIRED dl)
pkg_search_module(OpenGL REQUIRED gl)
pkg_search_module(X11 REQUIRED x11)

include_directories(${GLFW_INCLUDE_DIRS} ${OPENGL_INCLUDE_DIR} ${X11_INCLUDE_DIR})

target_link_libraries(picking ${GLFW_LIBRARIES} ${OPENGL_LIBRARIES} ${X11_LIBRARIES})
