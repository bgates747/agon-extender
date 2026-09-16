# Build ID is explicit and retained by the task's build manifest.
Import('env')
import os
identity=os.environ['R3_BUILD_ID']
assert identity.startswith('research003-reference-r01-b') and identity.endswith('Z')
env.Append(CPPDEFINES=[('R3_BUILD_ID', '\\"'+identity+'\\"')])
