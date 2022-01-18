Eng.

A test application that shows the advanced features of working with the library, including user units and working with the correction table.


For run:

 * On OS X: library is a Mac OS X framework, and at example application it’s bundled inside testapp_C.app.
Copy ximc/macosx/libximc.framework, ximc/ximc.h to the directory examples/testapp_C.
Install XCode. Test app should be built with XCode project testapp_C.xcodeproj.
Then launch application testapp_C.app and check activity output in Console.app.
 * For Linux: install libximc*deb and libximc-dev*dev of the target architecture in the specified order. Then copy ximc/ximc.h to the directory
examples/testapp_C. Install gcc. Test application can be built with the installed library with the following script:
$ make
In case of cross-compilation (target architecture differs from the current system architecture) feed -m64 or -m32 flag
to compiler.
Then launch the application as:
$ make run
 * In Windows: testapp_C can be built using testapp_C.sln. Make sure that Microsoft Visual C++ Redistributable Package 2013 is installed.
Open solution examples/testapp_C/testapp_C.sln, build and run from the IDE.



Rus.

Тестовое приложение показывающее расширенные возможности работы с библиотекой, включая пользовательские единицы и работу с корректирующей таблицей.

 
Для запуска примера:

* На OS X: библиотека для Mac OS поставляется в формате Mac OS X framework. Скопируйте ximc/macosx/libximc.framework, ximc/ximc.h в каталог
examples/testapp_C. Должен быть установлен XCode. Пример testapp_C дорлжен быть собран проектом XCode testapp_C.xcodeproj.
Запустите приложение testapp_C.app и проверте его работу в Console.app.
* Для Linux: установите libximc*deb и libximc-dev*dev целевой архитектуры в указанном порядке. Затем скопируйте ximc/ximc.h в каталог
examples/testapp_C. Установите gcc. Тестовое приложение может быть собрано с помощью установленной библиотеки командой:
$ make
Выполнить приложение можно командой:
$ make run
* В Windows для компиляции необходимо использовать MS Visual C++. Убедитесь, что Microsoft Visual C++ Redistributable Package 2013 установлен. 
Библиотека с зависимостями находится в папках ximc/win**. Для работы примера неоходимы следующие файлы: bindy.dll, libximc.dll, xiwrapper.dll.
Откройте пример /testapp_C/testapp_C.sln, соберите и запустите его из среды IDE.

