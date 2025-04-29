# utils/tf_stub.py
"""
伪造最小 TensorFlow 子集, 让 deepctr-torch 在没有
真正 TensorFlow 的环境下 (Windows / Py3.10) 也能 import.

导入一次即可:
    import utils.tf_stub
"""

import sys, types

# ---------- 创建模块骨架 ----------
mods = {
    "tensorflow",
    "tensorflow.python",
    "tensorflow.python.keras",
    "tensorflow.python.keras.callbacks",
    "tensorflow.python.keras._impl",
    "tensorflow.python.keras._impl.keras",
    "tensorflow.python.keras._impl.keras.callbacks",
}

for name in mods:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)

# ---------- 塞进 callbacks 所需的类 ----------
cb_mod      = sys.modules["tensorflow.python.keras.callbacks"]
cb_impl_mod = sys.modules["tensorflow.python.keras._impl.keras.callbacks"]

class _Dummy(object):
    def __init__(self, *_, **__): pass

_need = [
    "CallbackList",
    "EarlyStopping",
    "ReduceLROnPlateau",
    "ModelCheckpoint",
    "TensorBoard",
]

for cls in _need:
    setattr(cb_mod, cls, _Dummy)
    setattr(cb_impl_mod, cls, _Dummy)
