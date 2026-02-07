@echo off
REM Setup script for Hallucination Hunter

echo ======================================================================
echo HALLUCINATION HUNTER - Setup Script
echo ======================================================================

echo.
echo [1/3] Installing core dependencies...
pip install --only-binary :all: sentence-transformers chromadb transformers torch pydantic

echo.
echo [2/3] Installing API dependencies...
pip install fastapi uvicorn[standard] python-multipart

echo.
echo [3/3] Verifying installation...
python test_system.py

echo.
echo ======================================================================
echo Setup complete!
echo.
echo Next steps:
echo   1. Run complete pipeline: python pipeline.py
echo   2. Start API server: python api.py
echo   3. View README.md for full documentation
echo ======================================================================
pause
