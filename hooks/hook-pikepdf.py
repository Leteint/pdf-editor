# PyInstaller hook for pikepdf
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas          = collect_data_files('pikepdf')
hiddenimports  = collect_submodules('pikepdf')
