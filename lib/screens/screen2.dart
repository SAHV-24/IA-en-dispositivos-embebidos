import 'package:flutter/material.dart';

class Screen2 extends StatelessWidget {
  const Screen2({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Screen 2')),
      body: Center(
        child: ElevatedButton(
          // Equivalente a "when Button2.Click"
          onPressed: () {
            // Equivalente a "open another screen screenName Screen4"
            Navigator.pushNamed(context, '/screen4');
          },
          child: const Text('Conectar Dispositivo BLE (Ir a Screen 4)'),
        ),
      ),
    );
  }
}