$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$openOcd = Get-ChildItem -Path 'C:\ST\STM32CubeIDE*\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.openocd.win32*\tools\bin\openocd.exe' -File |
    Sort-Object FullName | Select-Object -Last 1
$scripts = Get-ChildItem -Path 'C:\ST\STM32CubeIDE*\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.debug.openocd*\resources\openocd\st_scripts' -Directory |
    Sort-Object FullName | Select-Object -Last 1
if (-not $openOcd -or -not $scripts) { throw 'CubeIDE OpenOCD components were not found.' }
Write-Host 'CMSIS-DAP GDB server: 127.0.0.1:3333. Close Keil Debug before connecting.'
Write-Host 'CubeIDE configuration: CMSIS_DAP_Attach. Ctrl+C stops this server.'
& $openOcd.FullName -s $scripts.FullName -f interface/cmsis-dap.cfg -f target/stm32l4x.cfg `
    -c 'adapter serial ATK-03262021' -c 'adapter speed 100' -c 'bindto 127.0.0.1' `
    -c 'tcl_port disabled' -c 'telnet_port disabled' `
    -c 'stm32l4.cpu configure -event gdb-attach {halt}' `
    -c 'stm32l4.cpu configure -event gdb-detach {resume}' -c init
exit $LASTEXITCODE
