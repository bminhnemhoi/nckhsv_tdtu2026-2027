@echo off
rem Build the CinC 2027 draft: pdflatex -> bibtex -> pdflatex x2.
rem Usage: build.bat           (normal build)
rem        build.bat clean     (remove auxiliary files first)
setlocal
cd /d "%~dp0"
if /i "%1"=="clean" (
  del /q main.aux main.bbl main.blg main.log main.out main.pdf 2>nul
)
pdflatex -interaction=nonstopmode -halt-on-error main.tex >nul || goto :fail
bibtex main >nul
pdflatex -interaction=nonstopmode -halt-on-error main.tex >nul || goto :fail
pdflatex -interaction=nonstopmode -halt-on-error main.tex >nul || goto :fail
findstr /c:"Output written" main.log
findstr /c:"undefined" main.log >nul && echo WARNING: undefined references, check main.log
echo done: main.pdf
exit /b 0
:fail
echo BUILD FAILED, see main.log
exit /b 1
