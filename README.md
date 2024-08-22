For documentation check: https://github.com/daid/Cura/wiki  
如需查看文档，请访问：https://github.com/daid/Cura/wiki

For downloads check: https://github.com/daid/Cura/downloads  
如需下载，请访问：https://github.com/daid/Cura/downloads

This package includes two programs:  
此软件包包含两个程序：

Pronterface:  
Pronterface：

    An application for both manually controlling and automatically feeding gcode to a 3D printer.  
    一个用于手动控制和自动向3D打印机传送GCode的应用程序。

Cura:  

   A easy to use program for slicing STL files using SkeinForge. Cura can also visualize the 3D models in a variety of ways.  
   一个使用SkeinForge切片STL文件的易用程序。Cura还可以通过多种方式可视化3D模型。

   On first run, Cura will ask to go through a set of calibration steps that will perform a series of operations on your 3D printer. One of those steps involves extruding a bit of filament where the filament is initially nearly fully extracted.  As such, it you will probably need to run Pronterface first, heat up the extruder enough to be able to extract the filament and then use the Pronterface interface to reverse the extruder motor until the filament is at the right position (specifically, until the filament end is even with where the Bowden tube leaves the extuder motor assembly, on an Ultimaker).  
   第一次运行时，Cura会要求进行一系列校准步骤，这些步骤会对您的3D打印机执行一系列操作。其中一步是挤出一些几乎完全抽出的细丝。因此，您可能需要先运行Pronterface，将挤出机加热到足以抽出细丝的程度，然后使用Pronterface界面反向挤出机电机，直到细丝到达正确的位置（特别是，直到细丝末端与Bowden管离开挤出机电机组件的位置齐平，对于Ultimaker）。

========  
BUILDING  
构建  
========  

    ./package.sh  

The build script defaults to building for Windows.  If you want to build for Mac OS X or Linux, choose one of:  
构建脚本默认构建Windows版本。如果您想构建Mac OS X或Linux版本，请选择以下之一：

    ./package.sh osx64  
    ./package.sh linux  

Note that Mac OS X currently requires the manual installation of wxPython, PySerial, and PyOpenGL:  
请注意，Mac OS X目前需要手动安装wxPython、PySerial和PyOpenGL：

    sudo easy_install-2.7 pyserial  
    sudo easy_install-2.7 PyOpenGL  

You will need to download the appropriate wxPython Installer package and install it.  It is available from:  
您需要下载相应的wxPython安装包并进行安装。下载地址：

    http://www.wxpython.org/download.php  

Specifically, install "wxPython2.9-osx-cocoa-py2.7" as it is the build that supports 64-bit execution.  
请特别安装 "wxPython2.9-osx-cocoa-py2.7"，因为它支持64位执行。

=======  
RUNNING  
运行  
=======  

Windows  
-------

Double-click skeinforge.bat and Printrun.bat.  
双击 skeinforge.bat 和 Printrun.bat。

Mac OS X & Linux  
----------------

Once built, the two apps -- Pronterface and Cura -- must be started from the command line (for now):  
一旦构建完成，这两个应用程序——Pronterface 和 Cura——必须从命令行启动（目前是这样）：

    # open a new terminal window and....  
    打开一个新的终端窗口并执行以下命令....
    cd osx64-Cura-NewUI-Beta4  
    ./pronterface.sh &  
    ./Cura.sh &  

This will start both applications with their console logging output directed into the terminal window.  
这将启动两个应用程序，并将它们的控制台日志输出重定向到终端窗口。

========  
FIRMWARE  
固件  
========  

For Ultimaker users, it is highly recommended -- nearly required -- that you upgrade your firmware to the latest Marlin builds.  See:  
对于Ultimaker用户，强烈建议——几乎是必须的——将固件升级到最新的Marlin版本。请参见：

    http://wiki.ultimaker.com/Skeinforge_PyPy