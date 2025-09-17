import 'dart:async';
import 'dart:typed_data';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';
import 'package:permission_handler/permission_handler.dart';
import 'prediction_screen.dart';

class Screen4 extends StatefulWidget {
  final bool restartGame;
  const Screen4({super.key, this.restartGame = false});

  @override
  State<Screen4> createState() => _Screen4State();
}

class _Screen4State extends State<Screen4> {
  // Log visual para debug
  final List<String> _eventLog = [];

  // Función para agregar eventos al log visual
  void _addLog(String msg) {
    setState(() {
      _eventLog.add(
        "[${DateTime.now().toIso8601String().substring(11, 19)}] $msg",
      );
      if (_eventLog.length > 30) _eventLog.removeAt(0);
    });
  }

  // --- Variables existentes ---
  final String serviceUuid = "19b10000-e8f2-537e-4f6c-d104768a1214";
  final String characteristicUuid = "19b10001-e8f2-537e-4f6c-d104768a1214";
  final List<String> referentList = [
    'n_reves.png',
    'r_reves.png',
    'sc.png',
    'y.png',
    'z_gorrito.png',
  ];

  String currentImage = 'assets/images/ready.png';
  String statusText = "Desconectado";
  BluetoothDevice? connectedDevice;
  List<ScanResult> scanResults = [];
  bool isScanning = false;
  final Random random = Random();
  StreamSubscription<BluetoothConnectionState>? connectionStateSubscription;
  Timer? _navigationTimer;

  // **NUEVO:** Variables para guardar la predicción y gestionar la escucha de datos
  String? _receivedPrediction;
  StreamSubscription<List<int>>? _valueSubscription;

  @override
  void initState() {
    super.initState();
    // Si venimos de "Jugar de Nuevo" y el dispositivo sigue conectado, reiniciamos el juego
    if (widget.restartGame && connectedDevice != null) {
      _restartGameAndSendCommand();
    }
  }

  void _restartGameAndSendCommand() async {
    // Resetear predicción y UI
    setState(() {
      _receivedPrediction = null;
      statusText = "Conectado";
      currentImage =
          'assets/images/' + referentList[random.nextInt(referentList.length)];
    });
    // Buscar el characteristic de control y enviar '1'
    if (connectedDevice != null) {
      List<BluetoothService> services = await connectedDevice!
          .discoverServices();
      for (var service in services) {
        if (service.uuid.toString().toLowerCase() == serviceUuid) {
          for (var characteristic in service.characteristics) {
            String uuid = characteristic.uuid.toString().toLowerCase();
            if (uuid == controlCharacteristicUuid) {
              await characteristic.write([0x01], withoutResponse: true);
              print("==> Enviado 0x01 al Arduino para reiniciar inferencia");
            }
          }
        }
      }
    }
    // Reiniciar el proceso de predicción
    _startPredictionProcess();
  }

  @override
  void dispose() {
    connectionStateSubscription?.cancel();
    _navigationTimer?.cancel();
    _valueSubscription?.cancel(); // Cancela la escucha de datos
    super.dispose();
  }

  Future<void> requestPermissions() async {
    await [
      Permission.location,
      Permission.bluetoothScan,
      Permission.bluetoothConnect,
    ].request();
  }

  void startScan() {
    // Asegura permisos antes de escanear (Android 12+ requiere permisos de BT en runtime)
    requestPermissions();
    setState(() {
      isScanning = true;
      scanResults = [];
    });
    FlutterBluePlus.startScan(timeout: const Duration(seconds: 5));
    FlutterBluePlus.scanResults.listen((results) {
      setState(() {
        scanResults = results;
      });
    });
  }

  void connectToDevice(BluetoothDevice device) async {
    // La lógica de conexión es la misma, solo que ahora llama a la nueva función
    await FlutterBluePlus.stopScan();
    _addLog('Intentando conectar a ${device.platformName}');
    connectionStateSubscription = device.connectionState.listen((state) async {
      if (state == BluetoothConnectionState.connected) {
        setState(() {
          connectedDevice = device;
        });
        _addLog('Conectado a ${device.platformName}');
        _startPredictionProcess();
        discoverServices(device);
      } else if (state == BluetoothConnectionState.disconnected) {
        _navigationTimer?.cancel();
        _valueSubscription?.cancel();
        setState(() {
          connectedDevice = null;
          statusText = "Desconectado";
        });
        _addLog('Desconectado de ${device.platformName}');
      }
    });
    try {
      await device.connect(timeout: const Duration(seconds: 15));
    } catch (e) {
      _addLog('Error al conectar: $e');
      connectionStateSubscription?.cancel();
    }
  }

  // **FUNCIÓN COMPLETAMENTE NUEVA Y MODIFICADA**
  void _startPredictionProcess() {
    // 1. Resetea la predicción anterior
    _receivedPrediction = null;

    // 2. Muestra la letra aleatoria en la UI
    setState(() {
      statusText = "Conectado";
      currentImage =
          'assets/images/${referentList[random.nextInt(referentList.length)]}';
    });
    // La navegación ahora depende solo de la recepción de datos BLE
  }

  final String controlCharacteristicUuid =
      "19b10002-e8f2-537e-4f6c-d104768a1214";

  void discoverServices(BluetoothDevice device) async {
    try {
      List<BluetoothService> services = await device.discoverServices();

      BluetoothCharacteristic? resultChar;
      BluetoothCharacteristic? controlChar;

      for (var service in services) {
        if (service.uuid.toString().toLowerCase() == serviceUuid) {
          for (var ch in service.characteristics) {
            final uuid = ch.uuid.toString().toLowerCase();
            if (uuid == characteristicUuid) resultChar = ch;
            if (uuid == controlCharacteristicUuid) controlChar = ch;
          }
        }
      }

      if (resultChar == null || controlChar == null) {
        _addLog("Característica(s) no encontradas en el servicio BLE");
        return;
      }

      // 1) Suscribirse a notificaciones ANTES de enviar el comando para no perder el único aviso
  await resultChar.setNotifyValue(true);
      _valueSubscription?.cancel();
      _addLog('Esperando dato de inferencia...');
  _valueSubscription = resultChar.onValueReceived.listen((value) {
        // El firmware usa BLEIntCharacteristic -> suele enviar Int32 LE
        int receivedInt = 0;
        if (value.isEmpty) {
          receivedInt = 0;
        } else if (value.length >= 4) {
          final bytes = Uint8List.fromList(value);
          final bd = ByteData.view(bytes.buffer);
          receivedInt = bd.getInt32(0, Endian.little);
        } else {
          // Fallback si envía un solo byte
          receivedInt = value[0];
        }
        _addLog('Dato recibido (len=${value.length}): $receivedInt');
        handlePrediction(receivedInt.toString());
      });

      // 2) Ahora sí, enviar el comando 0x01 para iniciar la inferencia
      try {
        await controlChar.write([0x01], withoutResponse: false);
        print("==> Enviado 0x01 al Arduino para iniciar inferencia");
      } catch (e) {
        // Algunos dispositivos requieren withoutResponse:true
        await controlChar.write([0x01], withoutResponse: true);
        print("==> Enviado 0x01 (sin respuesta) al Arduino");
      }
    } catch (e) {
      print("==> ERROR al descubrir servicios: $e");
    }
  }

  void handlePrediction(String prediction) {
    // Guarda la última predicción recibida y navega a la pantalla de resultados
    _addLog('Mostrando resultado: $prediction');
    _receivedPrediction = prediction;
    if (mounted) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) =>
              PredictionScreen(prediction: _receivedPrediction ?? "0"),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Conexión BLE")),
      body: Center(child: _buildUI()),
    );
  }

  // Función para decidir qué mostrar en la pantalla según el estado
  // Función para decidir qué mostrar en la pantalla según el estado
  Widget _buildUI() {
    if (connectedDevice != null) {
      // === VISTA CONECTADA (DISEÑO AZUL Y LOG DEBUG) ===
      return Container(
        color: Colors.blue.shade50,
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.bluetooth_connected,
                  color: Colors.blue.shade700,
                  size: 32,
                ),
                const SizedBox(width: 10),
                Text(
                  statusText,
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 30),
            Image.asset(currentImage, height: 200),
            const SizedBox(height: 30),
            const Text(
              "Memoriza la letra...",
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Colors.blue,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              "Esperando resultado de inferencia...",
              style: TextStyle(fontSize: 20, color: Colors.blueGrey),
            ),
            const SizedBox(height: 30),
            // Log visual para debug
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade100,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "Log de eventos:",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.blue,
                    ),
                  ),
                  ..._eventLog.reversed
                      .take(6)
                      .map(
                        (e) => Text(
                          e,
                          style: const TextStyle(
                            fontSize: 14,
                            color: Colors.black87,
                          ),
                        ),
                      )
                      .toList(),
                ],
              ),
            ),
          ],
        ),
      );
    } else {
      // === VISTA PARA ESCANEAR Y CONECTAR (SIN CAMBIOS) ===
      return Column(
        children: [
          ElevatedButton(
            onPressed: startScan,
            child: Text(isScanning ? 'Escaneando...' : 'Escanear Dispositivos'),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: scanResults.length,
              itemBuilder: (context, index) {
                return ListTile(
                  title: Text(
                    scanResults[index].device.platformName.isNotEmpty
                        ? scanResults[index].device.platformName
                        : 'Dispositivo desconocido',
                  ),
                  subtitle: Text(scanResults[index].device.remoteId.toString()),
                  onTap: () => connectToDevice(scanResults[index].device),
                );
              },
            ),
          ),
        ],
      );
    }
  }
}
