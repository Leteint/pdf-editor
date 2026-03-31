# PyInstaller hook for pypdfium2
# Ensures the native pdfium shared library is collected.
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

datas    = collect_data_files('pypdfium2', include_py_files=False)
binaries = collect_dynamic_libs('pypdfium2')
