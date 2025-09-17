import 'package:flutter/material.dart';

class Screen1 extends StatelessWidget {
  const Screen1({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blue.shade50,
      appBar: AppBar(
        backgroundColor: Colors.blue.shade700,
        elevation: 0,
        title: const Text('VoxMarker', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 28, color: Colors.white, letterSpacing: 2)),
        centerTitle: true,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'VoxMarker',
              style: TextStyle(
                fontSize: 48,
                fontWeight: FontWeight.bold,
                color: Colors.blue.shade700,
                letterSpacing: 4,
                shadows: [
                  Shadow(
                    blurRadius: 12,
                    color: Colors.blue.shade200,
                    offset: Offset(0, 4),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 40),
            ElevatedButton.icon(
              icon: const Icon(Icons.bluetooth_searching, size: 28),
              label: const Text('Buscar Dispositivos', style: TextStyle(fontSize: 20)),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                backgroundColor: Colors.blue.shade700,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                elevation: 8,
              ),
              onPressed: () {
                Navigator.pushNamed(context, '/screen2');
              },
            ),
          ],
        ),
      ),
    );
  }
}