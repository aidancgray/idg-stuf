Eng.

This example shows how to work with a profile for a specific positioner in the user program.


For run:

 * On OS X: library is a Mac OS X framework, and at example application it’s bundled inside testprofile_C.app.
Copy ximc/macosx/libximc.framework, ximc/ximc.h to the directory examples/testprofile_C.
Install XCode. Test app should be built with XCode project testprofile_C.xcodeproj.
Then launch application testprofile_C.app and check activity output in Console.app.
 * For Linux: Install libximc*deb and libximc-dev*dev of the target architecture. Then copy ximc/ximc.h to the directory
examples/testprofile_C. Install gcc. Test application can be built with the installed library with the following script:
$ make
In case of cross-compilation (target architecture differs from the current system architecture) feed -m64 or -m32 flag
to compiler.
Then launch the application as:
$ make run
 * In Windows: testprofile_C can be built using testprofile_C.sln. Make sure that Microsoft Visual C++ Redistributable Package 2013 is installed.
Open solution examples/testprofile_C/testprofile_C.sln, build and run from the IDE.



Rus.

Данный пример показывает как работать с профилем для конкретного позиционера в пользовательском приложении.

 
Для запуска примера:

* На OS X: библиотека для Mac OS поставляется в формате Mac OS X framework. Скопируйте ximc/macosx/libximc.framework, ximc/ximc.h в каталог
examples/testprofile_C. Должен быть установлен XCode. Пример testprofile_C дорлжен быть собран проектом XCode testprofile_C.xcodeproj.
Запустите приложение testprofile_C.app и проверте его работу в Console.app.
* Для Linux: установите libximc*deb и libximc-dev*dev целевой архитектуры. Затем скопируйте ximc/ximc.h в каталог
examples/testprofile_C. Установите gcc. Тестовое приложение может быть собрано с помощью установленной библиотеки командой:
$ make
Выполнить приложение можно командой:
$ make run
* В Windows для компиляции необходимо использовать MS Visual C++. Убедитесь, что Microsoft Visual C++ Redistributable Package 2013 установлен. 
Библиотека с зависимостями находится в папках ximc/win**. Для работы примера неоходимы следующие файлы: bindy.dll, libximc.dll, xiwrapper.dll.
Откройте пример /testprofile_C/testprofile_C.sln, создайте и запустите их из среды IDE.

