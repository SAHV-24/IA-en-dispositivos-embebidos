// lib/screens/prediction_screen.dart

import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import 'screen4.dart'; // 👈 importa la pantalla del juego

class PredictionScreen extends StatefulWidget {
  final String prediction;

  const PredictionScreen({super.key, required this.prediction});

  @override
  State<PredictionScreen> createState() => _PredictionScreenState();
}

class _PredictionScreenState extends State<PredictionScreen> {
  String? resultImage;
  String? resultText;
  String? resultSound;
  final player = AudioPlayer();

  @override
  void initState() {
    super.initState();
    _processPrediction();

    // Reproduce sonido correspondiente
    if (resultSound != null) {
      player.play(AssetSource(resultSound!.replaceFirst('assets/', '')));
    }
  }

  void _processPrediction() {
    if (widget.prediction.toString() == "1") {
      resultImage = 'assets/images/n_reves.png';
      resultText = "музей - Museo🏛️";
      resultSound = 'assets/audio/n_reves.mp3';
    } else if (widget.prediction.toString() == "2") {
      resultImage = 'assets/images/r_reves.png';
      resultText = "Россиянин - Ruso 🪆";
      resultSound = 'assets/audio/r_reves.mp3';
    } else if (widget.prediction.toString() == "3") {
      resultImage = 'assets/images/sc.png';
      resultText = "помощь - Ayuda 🆘";
      resultSound = 'assets/audio/sc.mp3';
    } else if (widget.prediction.toString() == "4") {
      resultImage = 'assets/images/y.png';
      resultText = "Мыло - Jabón 🧼";
      resultSound = 'assets/audio/y.mp3';
    } else if (widget.prediction.toString() == "5") {
      resultImage = 'assets/images/z_gorrito.png';
      resultText = "жизнь - Vida 🍃";
      resultSound = 'assets/audio/z_gorrito.mp3';
    } else {
      resultImage = 'assets/images/equivocado.png';
      resultText = "No se detectó una predicción. ¡Inténtalo de nuevo!";
      resultSound = 'assets/audio/incorrecto.mp3';
    }
  }

  @override
  Widget build(BuildContext context) {
    if (resultImage == null || resultText == null) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      backgroundColor: Colors.blue.shade50,
      appBar: AppBar(
        title: const Text("VoxMarker", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 28, color: Colors.white, letterSpacing: 2)),
        centerTitle: true,
        backgroundColor: Colors.blue.shade700,
        elevation: 0,
        automaticallyImplyLeading: false,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                "El resultado es:",
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.blue.shade700),
              ),
              const SizedBox(height: 20),
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [BoxShadow(color: Colors.blue.shade100, blurRadius: 12, offset: Offset(0, 4))],
                ),
                padding: const EdgeInsets.all(24),
                child: Image.asset(resultImage!, height: 150),
              ),
              const SizedBox(height: 30),
              Text(
                resultText!,
                style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Colors.blue),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 40),
              ElevatedButton.icon(
                icon: const Icon(Icons.refresh, size: 24),
                label: const Text('Jugar de Nuevo', style: TextStyle(fontSize: 20)),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  backgroundColor: Colors.blue.shade700,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  elevation: 8,
                ),
                onPressed: () {
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (context) => const Screen4(restartGame: true)),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
