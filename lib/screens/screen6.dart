import 'dart:math';
import 'package:flutter/material.dart';

class Screen6 extends StatefulWidget {
  const Screen6({super.key});

  @override
  State<Screen6> createState() => _Screen6State();
}

class _Screen6State extends State<Screen6> {
  // Equivalente a la lista global "fun_facts"
  final List<String> funFacts = [
    "Todas las palabras del idioma ruso que empiezan por 'a' son préstamos de otros idiomas.",
    "Es habitual que las palabras del idioma ruso tengan más de una 'o' en su escritura.",
    "Si quieres convertirte en astronauta, tendrás que saber ruso.",
    "El número uno (один) tiene una forma plural que se usa con objetos que solo existen en plural.",
    "El 10% del vocabulario ruso está formado por extranjerismos.",
    "El verbo 'Tener' en ruso existe pero apenas se usa."
  ];

  String displayedFact = "";

  @override
  void initState() {
    super.initState();
    // Equivalente a "when Screen6.Initialize"
    _setRandomFact();
  }

  void _setRandomFact() {
    final random = Random();
    // Equivalente a "select list item ... index random"
    setState(() {
      displayedFact = funFacts[random.nextInt(funFacts.length)];
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Dato Curioso")),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Center(
          child: Text(
            displayedFact,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 22),
          ),
        ),
      ),
    );
  }
}