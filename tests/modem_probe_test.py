"""Check the actual retained-evidence validator, including plausible false passes."""
import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_modem_probe import validate
def good():
 r=[{'event':'start','build':'test','tx':47,'rx':48,'baud':115200}]
 for n in range(1,6):
  raw=b'\r\nAT version:1.3\r\nOK\r\n' if n==2 else b'\r\nOK\r\n'
  r.extend([{'event':'tx','seq':n,'hex':(b'AT+GMR\r\n' if n==2 else b'AT\r\n').hex()},
            {'event':'rx','seq':n,'hex':raw.hex()},
            {'event':'command_result','seq':n,'pass':True,'terminal':1,'identity':True,'bytes':len(raw)}])
 return r+[{'event':'end','pass':True,'uart_retired':True}]
class Validator(unittest.TestCase):
 def test_good(self):self.assertTrue(validate(good(),'test')['pass'])
 def test_failures(self):
  for kind in ['incomplete','duplicate','wrong_pin','error','no_retirement','false_ok','wrong_command','missing_identity']:
   with self.subTest(kind=kind):
    r=copy.deepcopy(good())
    if kind=='incomplete':r.pop(3)
    elif kind=='duplicate':r.insert(1,dict(r[0]))
    elif kind=='wrong_pin':r[0]['rx']=47
    elif kind=='error':r.insert(2,{'event':'uart_error'})
    elif kind=='no_retirement':r[-1]['uart_retired']=False
    elif kind=='false_ok':r[2]['hex']=b'SOME_OK_TEXT'.hex()
    elif kind=='wrong_command':r[1]['hex']=b'AT+RST\r\n'.hex()
    elif kind=='missing_identity':r[5]['hex']=b'\r\nOK\r\n'.hex();r[6]['bytes']=6
    with self.assertRaises((AssertionError,KeyError)):validate(r,'test')
if __name__=='__main__':unittest.main()
