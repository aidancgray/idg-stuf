Eng.


For run:
1. Change the current directory to examples/test_Python/standardtest. To use the libximc library correctly, the example uses a file wrapper, /ximc/crossplatform/wrappers/python/pyximc.py with a description of the library structure.
2. Configuring dependencies:
 * On OS X: copy the ximc/macosx/libximc library.add the framework to the current directory.
 * On Linux:
	- you can not install anything if you run the example using a batch file ./testpython.sh.
	- you must install the packages, from the /xbmc/deb archive folder, libximc7_x.x.x and libximc7-dev_x.x.x for the required architecture strictly in the specified order. You will also need to set LD_LIBRARY_PATH so that Python can find libraries using PATH. For example, using:
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:usr/lib. You must specify the correct path for the installed packages.
 * In Windows, you do not need to do anything before starting. All the necessary dependencies are in the example code. Used libraries: bindy.dll files libximc.dll xiwrapper.dll, keyfile.sqlite. Located in the folder for the corresponding versions of Windows.
3. To run, you need to have python 2 or 3 versions installed.
4. Run the example with the command:
python testpython.py


For modify:
The example code can be modified in any text editor.


Rus.

 
Для запуска примера:
1. Измените текущий каталог на examples/test_Python/standardtest. Для корректного использования библиотеки libximc в примере используется файловая оболочка, /ximc/crossplatform/wrappers/python/pyximc.py с описанием структуры библиотеки.
2. Настройка зависимостей:
 * В OS X: скопируйте библиотеку ximc/macosx/libximc.framework в текущий каталог.
 * В Linux: 
	- можно ни чего не устанавливать, если запускать пример с помощью командного файла ./testpython.sh
	- необходимо установить пакеты, из папки /ximc/deb архива, libximc7_x.x.x и libximc7-dev_x.x.x для требуемой архитектуры строго в указанном порядке. Так же потребуется установить LD_LIBRARY_PATH, чтобы Python мог находить библиотеки с помощью RPATH. Например, с помощью:
 export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:usr/lib - указать правильный путь для установленных пакетов.
 * В Windows перед запуском ничего не нужно делать. Все необходимые зависимости есть в коде примера. Используемые библиотеки: bindy.dll файлы libximc.dll xiwrapper.dll, keyfile.sqlite. Находится в папке для соответствующих версий Windows.
3. Для запуска необходим установленный python 2 или 3 версии.
4. Запустите пример командой:
 python testpython.py

 
Для модификации примера:
Код примера можно модифицировать в любом текстовом редакторе.