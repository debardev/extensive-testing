:: -------------------------------------------------------------------
:: Copyright (c) 2010-2018 Denis Machard
:: This file is part of the extensive testing project
::
:: This library is free software; you can redistribute it and/or
:: modify it under the terms of the GNU Lesser General Public
:: License as published by the Free Software Foundation; either
:: version 2.1 of the License, or (at your option) any later version.
::
:: This library is distributed in the hope that it will be useful,
:: but WITHOUT ANY WARRANTY; without even the implied warranty of
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
:: Lesser General Public License for more details.
::
:: You should have received a copy of the GNU Lesser General Public
:: License along with this library; if not, write to the Free Software
:: Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
:: MA 02110-1301 USA
:: -------------------------------------------------------------------

@echo off

set Project=%~dp0..\..\

set PythonPath=C:\Python36
set Python=%PythonPath%\python.exe
set Output=D:\My Lab\outputs\

:: make resources
%PythonPath%\python.exe -m PyQt5.pyrcc_main -o "%Project%\Resources\Resources.py" "%Project%\Resources\__resources.qrc"

:: build the project
echo Build the project...
cd "%Project%"
%Python% "%Project%\ConfigureExe.py"
%PythonPath%\Scripts\pyinstaller.exe --clean --noconfirm BuildWinIns.spec

:: build the installer
echo Build the installer...
"%Python%" "%Project%\BuildWinInno.py" "%Output%\" "dist\ExtensiveTestingToolbox"


pause