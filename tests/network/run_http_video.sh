#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
output=$(mktemp -d)
trap 'rm -rf "$output"' EXIT
${CXX:-g++} -std=c++17 -Wall -Wextra -Werror -pthread -fsanitize=address,undefined -fno-omit-frame-pointer -no-pie \
 -DCONFIG_HTTPD_WS_SUPPORT=1 -DCONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT=1 \
 -I tests/network/http_fakes -I vdp/video tests/network/http_video_service_test.cpp \
 vdp/video/extender/network/{http_video_service,browser_video_service_core,opaque_message}.cpp -o "$output/check"
"$output/check"
${CXX:-g++} -std=c++17 -Wall -Wextra -Werror -pthread -fsanitize=address,undefined -fno-omit-frame-pointer -no-pie \
 -DCONFIG_HTTPD_WS_SUPPORT=1 -DCONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT=1 -DAGON_EXTENDER_HDMI \
 -I tests/network/http_fakes -I vdp/video tests/network/http_video_service_test.cpp \
 vdp/video/extender/network/{http_video_service,browser_video_service_core,opaque_message}.cpp -o "$output/hdmi-check"
"$output/hdmi-check"
