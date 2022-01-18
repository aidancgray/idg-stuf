Eng.

This example demonstrates loading python profiles into the controller.


For run:
1. Change the current directory to examples/test_Python/profiletest. To use the libximc library correctly, the example uses a file wrapper, /ximc/crossplatform/wrappers/python/pyximc.py with a description of the library structure.
2. Configuring dependencies:
 * On OS X: copy the ximc/macosx/libximc library.add the framework to the current directory.
 * On Linux:
	- you can not install anything if you run the example using a batch file ./testpythonprofile.sh.
	- you may need to set LD_LIBRARY_PATH so that Python can find libraries using RPATH. For example, using:
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH: 'pwd'
 * In Windows, you do not need to do anything before starting. All the necessary dependencies are in the example code. Used libraries: bindy.dll files libximc.dll xiwrapper.dll, keyfile.sqlite. Located in the folder for the corresponding versions of Windows.
3. To run, you need to have python 2 or 3 versions installed.
4. Run the example with the command:
python testpythonprofile.py


For modify:
1. The example code can be modified in any text editor.
2. To use a different profile, copy the required profile from the \ximc\python-profiles folder to examples/test_Python/profiletest. In the example code, replace the profile name with the required one.


Rus.

Этот пример демонстрирует загрузку профилей для питона в контроллер.

 
Для запуска примера:
1. Измените текущий каталог на examples/test_Python/profiletest. Для корректного использования библиотеки libximc в примере используется файловая оболочка, /ximc/crossplatform/wrappers/python/pyximc.py с описанием структуры библиотеки.
2. Настройка зависимостей:
 * В OS X: скопируйте библиотеку ximc/macosx/libximc.framework в текущий каталог.
 * В Linux: 
	- можно ни чего не устанавливать, если запускать пример с помощью командного файла ./testpythonprofile.sh
	- возможно, вам потребуется установить LD_LIBRARY_PATH, чтобы Python мог находить библиотеки с помощью RPATH. Например, с помощью:
 export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:'pwd'
 * В Windows перед запуском ничего не нужно делать. Все необходимые зависимости есть в коде примера. Используемые библиотеки: bindy.dll файлы libximc.dll xiwrapper.dll. Находится в папке для соответствующих версий Windows.
3. Для запуска необходим установленный python 2 или 3 версии.
4. Запустите пример командой:
 python testpythonprofile.py

 
Для модификации примера:
1. Код примера можно модифицировать в любом текстовом редакторе.
2. Для использования другого профиля, скопируйте необходимый профиль из папки \ximc\python-profiles в examples/test_Python/profiletest. В коде примера замените имя профиля на необходимое.
