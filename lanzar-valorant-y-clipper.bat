@echo off
cd /d "%~dp0"
echo === Lanzando VALORANT (--launch-product=valorant --launch-patchline=live) + VANTS Clipper ===
python vants_clipper.py --launch-valorant
pause
