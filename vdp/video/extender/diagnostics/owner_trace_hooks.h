// Inject only into the isolated __idf_freertos C target. ESP-IDF5.5.5
// FreeRTOS-Kernel/tasks.c exposes pxCurrentTCBs at these official trace sites.
#pragma once
#ifndef __ASSEMBLER__
#ifdef __cplusplus
extern "C" {
#endif
void agon_owner_switch(unsigned core,unsigned kind,void *task,const char *name,unsigned priority);
#ifdef __cplusplus
}
#endif
#define AGON_OWNER_SWITCH(kind) do { unsigned c=portGET_CORE_ID(); agon_owner_switch(c,kind,(void*)pxCurrentTCBs[c],pxCurrentTCBs[c]->pcTaskName,pxCurrentTCBs[c]->uxPriority); } while(0)
#define traceTASK_SWITCHED_IN() AGON_OWNER_SWITCH(1)
#define traceTASK_SWITCHED_OUT() AGON_OWNER_SWITCH(0)
#endif
