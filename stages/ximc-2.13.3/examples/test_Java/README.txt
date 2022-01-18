Eng.


For run:
1. To run the example for win32 or win64, you need to register the path to the Java developer's applications in the system paths, then type in the command line:
 java -classpath libjximc.jar -classpath test_Java.jar ru.ximc.TestJava
2. For other platforms, use the compiled folder. You may need to copy some dependencies to it.
 
For modify:
1. Unpack jar:
 jar xvf test_Java.jar ru META-INF
2. Modyfy sources
3. Build example:
 javac -classpath libjximc.jar -Xlint ru/ximc/TestJava.java
 jar cmf META-INF\MANIFEST.MF test_Java.jar ru
 
 When assembling the example, it is necessary to pay attention to the fact that only one path to the Java developer's system is registered in the system paths, otherwise a situation may arise when compilation will be performed by one version of the package, 
 and assembly or execution by another, which may lead to errors.

Rus.

 
Для запуска примера:
1. Для запуска примера для win32 или win64 необходимо прописать путь к приложениям разработчика Java в системные пути, после чего наберите в командной строке: 
 java -classpath libjximc.jar -classpath test_Java.jar ru.ximc.TestJava
2. Для других платформ используйте папку compiled. Возможно в нее понадобится скопировть некоторые зависимости.
 
Для модификации примера:
1. Распакуйте jar командой:
 jar xvf test_Java.jar ru META-INF
2. Модифицируйте исходные коды
3. Соберите пример:
 javac -classpath libjximc.jar -Xlint ru/ximc/TestJava.java
 jar cmf META-INF/MANIFEST.MF test_Java.jar ru
 
 При сборке примера необходимо обратить внимание, чтобы в системных путях был прописан только один путь к системе разработчика Java, в противном случае может возникнуть ситуация когда компиляция будет производится одной версией пакета,
 а сборка или выполнение другой, что может привести к ошибкам.