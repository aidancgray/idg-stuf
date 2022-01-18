Eng.


For run:
1. Before launch:
 * On OS X: copy ximc/macosx/libximc.framework, ximc/macosx/wrappers/ximcm.h, ximc/ximc.h to the directory
examples/test_MATLAB. Install XCode compatible with Matlab.
 * On Linux: install libximc*deb and libximc-dev*dev of target architecture. Then copy ximc/macosx/wrappers/ximcm.h
to the directory examples/test_MATLAB. Install gcc compatible with Matlab.
For XCode and gcc version compability check document https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/support/sysreq/files/SystemRequirements-Release2014a_SupportedCompilers.pdf or similar.
 * On Windows before the start nothing needs to be done. Change current directory in the MATLAB to the examples/matlab.
 The library with dependencies is located in the ximc/win** folders. For the example to work, you need the following files: bindy.dll, libximc.dll, xiwrapper.dll, keyfile.sqlite.
2. Then launch in MATLAB prompt.

For modify:
The example code can be modified in MATLAB editor.


Rus.

 
Для запуска примера:
1. Перед запуском:
* На OS X: скопируйте ximc/macosx/libximc.framework, ximc/macosx/wrappers/ximcm.h, ximc/ximc.h в каталог
examples/test_MATLAB. Установите XCode, совместимый с Matlab.
* Для Linux: установите libximc*deb и libximc-dev*dev целевой архитектуры. Затем скопируйте ximc/macosx/wrappers/ximcm.h
в каталог examples/test_MATLAB. Установите gcc, совместимый с Matlab.
Для проверки совместимости версий XCode и gcc изучите документы https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/support/sysreq/files/SystemRequirements-Release2014a_SupportedCompilers.pdf или аналогичные.
* В Windows перед запуском ничего не нужно делать. Изменить текущий каталог в среде MATLAB в examples/matlab.
Библиотека с зависимостями находится в папках ximc/win**. Для работы примера неоходимы следующие файлы: bindy.dll, libximc.dll, xiwrapper.dll, keyfile.sqlite.
2. Затем запустите программу в командной строке MATLAB.

 
Для модификации примера:
Код примера можно модифицировать в редакторе MATLAB.