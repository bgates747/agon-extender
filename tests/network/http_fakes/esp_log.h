#pragma once
template<class... T> inline void log_fake(T...) {}
#define ESP_LOGI(...) log_fake(__VA_ARGS__)
#define ESP_LOGW(...) log_fake(__VA_ARGS__)
#define ESP_LOGE(...) log_fake(__VA_ARGS__)
