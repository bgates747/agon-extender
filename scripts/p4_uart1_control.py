"""Task-private paired UART1 half-baud source gate; never accesses hardware."""
import json
from pathlib import Path

def check(root: Path):
    path=root/'vdp/native/uart1-baud-control.json'
    record=json.loads(path.read_text())
    if record != dict(schema='net004-paired-uart1-control-v1', status='experimental-source-only', uart0_baud=1152000, uart1_baud=576000, frame='8N1', flow_control='RTS/CTS', paired_firmware_required=True, ordinary_default_adoption=False):
        raise ValueError('Paired control declaration differs')
    source=(root/'vdp/video/extender/transport/console_hardware.inc').read_text()
    if source.count('cfg.baud_rate=576000;cfg.data_bits=UART_DATA_8_BITS;')!=1 or 'UART1 576000 8N1 RTS/CTS' not in source:
        raise ValueError('P4 setup and boot identity must both select576000')
    if 'uart_param_config(UART_NUM_1,&cfg)' not in source:
        raise ValueError('Paired control must configure physical UART_NUM_1')
    return record
