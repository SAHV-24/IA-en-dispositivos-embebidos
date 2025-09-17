import 'package:flutter/material.dart';
import '../screens/screen1.dart';
import '../screens/screen2.dart';
import '../screens/screen4.dart';
import '../screens/screen6.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BLE App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      // Definimos las rutas de navegación
      initialRoute: '/',
      routes: {
        '/': (context) => const Screen1(),
        '/screen2': (context) => const Screen2(),
        '/screen4': (context) => const Screen4(),
        '/screen6': (context) => const Screen6(),
      },
    );
  }
}