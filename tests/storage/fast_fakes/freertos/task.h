#pragma once
#include "FreeRTOS.h"
extern TaskFunction_t pendingWorker;
void processQueue();
inline void vTaskDelay(unsigned){processQueue();}
inline BaseType_t xTaskCreatePinnedToCore(TaskFunction_t f,const char *,uint32_t,void *,UBaseType_t,TaskHandle_t *,BaseType_t){pendingWorker=f;return pdPASS;}
inline void vTaskDelete(TaskHandle_t){}
