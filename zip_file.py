import zipfile
import os

exe_path = r'F:\Cliquey\Cliquey-DTAI-Judge\examples\agents\bot10\Cliquey'
zip_path = r'F:\Cliquey\Cliquey-DTAI-Judge\examples\agents\bot10\Cliquey.zip'

with zipfile.ZipFile(zip_path, 'w') as zipf:
    zipf.write(exe_path, os.path.basename(exe_path))
