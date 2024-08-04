import 'dart:convert';
import 'dart:io';
import 'package:client_side/views/scatter_chart.dart';
import 'package:flutter/material.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late String serverIp = "127.0.0.1";
  late int port = 0;
  final GlobalKey<ShotScatterChartState> scatterChartKey =
      GlobalKey<ShotScatterChartState>();
  Socket? _socket;
  List<Offset> corners = [];

  @override
  void dispose() {
    super.dispose();
    _closeSocket();
  }

  bool _isValidIPv4(String ip) {
    final RegExp ipv4RegExp = RegExp(
        r'^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])\.' // First octet
        r'(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])\.' // Second octet
        r'(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])\.' // Third octet
        r'(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])$' // Fourth octet
        );
    return ipv4RegExp.hasMatch(ip);
  }

  void _updateChartData(List<MapEntry<double, double>> newData) {
    final scatterChartState = scatterChartKey.currentState;
    scatterChartState?.updateData(newData);
  }

  void _clearChart() {
    final scatterChartState = scatterChartKey.currentState;
    scatterChartState?.clearData();
  }

  void _setChartScale() {
    final scatterChartState = scatterChartKey.currentState;
    scatterChartState?.setScale(corners);
  }

  void _connectToServer() async {
    _clearChart();
    if (_socket != null) {
      _closeSocket();
    }

    try {
      _socket = await Socket.connect(serverIp, port);
      _socket?.listen((data) {
        String dataString = utf8.decode(data);
        if (dataString.startsWith("CORNERS:")) {
          // Handle corners
          String cornersData = dataString.substring(8).trim();
          List<String> cornerStrings = cornersData.split(',');
          corners = List.generate(cornerStrings.length ~/ 2, (i) {
            double x = double.parse(cornerStrings[i * 2]);
            double y = double.parse(cornerStrings[i * 2 + 1]);
            return Offset(x, y);
          });
          print("Received corners: $corners");
          _setChartScale(); // Update the chart scale after receiving corners
        } else {
          // Handle shot positions
          List<String> values = dataString.trim().split(",");
          if (values.length == 2) {
            double x = double.tryParse(values[0]) ?? 0.0;
            double y = double.tryParse(values[1]) ?? 0.0;
            _updateChartData([MapEntry(x, y)]);
            // print("($x, $y)");
          }
        }
      }, onError: (error) {
        print("Socket error: $error");
      }, onDone: () {
        print("Socket closed");
      });
    } catch (e) {
      print("Error $e");
    }
  }

  void _closeSocket() {
    _socket?.close();
    _socket = null;
  }

  void _showConnectionDialog() {
    String newIp = serverIp;
    int newPort = port;

    TextEditingController ipController = TextEditingController(text: serverIp);
    TextEditingController portController =
        TextEditingController(text: port.toString());

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Center(
            child: Text(
              "Connect to camera",
              textAlign: TextAlign.center,
            ),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                "Camera IP:",
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              TextField(
                controller: ipController,
                keyboardType: TextInputType.name,
                onChanged: (value) {
                  if (_isValidIPv4(value)) {
                    newIp = value;
                  } else {
                    newIp = serverIp;
                  }
                },
              ),
              const SizedBox(
                height: 5,
              ),
              const Text(
                "Camera port:",
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              TextField(
                controller: portController,
                keyboardType: TextInputType.number,
                onChanged: (value) {
                  if (int.tryParse(value) != null) {
                    if (int.parse(value) >= 0 && int.parse(value) <= 65535) {
                      newPort = int.parse(value);
                    }
                  }
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: const Text("Cancel"),
            ),
            TextButton(
              onPressed: () {
                setState(() {
                  serverIp = newIp;
                  port = newPort;
                });
                _connectToServer();
                Navigator.of(context).pop();
              },
              child: const Text("Save"),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Shot tracker",
          style: TextStyle(
            color: Colors.white,
            fontSize: 30,
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor: const Color.fromARGB(255, 20, 95, 235),
      ),
      body: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Align(
              alignment: Alignment.centerLeft,
              child: Row(
                children: [
                  Tooltip(
                    message: "Connect to camera",
                    child: ElevatedButton(
                      onPressed: () {
                        _showConnectionDialog();
                      },
                      style: ButtonStyle(
                        backgroundColor:
                            WidgetStateProperty.all<Color>(Colors.blueAccent),
                      ),
                      child: const Icon(
                        Icons.connected_tv_outlined,
                        color: Colors.white,
                      ),
                    ),
                  ),
                  const SizedBox(
                    width: 15,
                  ),
                  Tooltip(
                    message: "Clear chart",
                    child: ElevatedButton(
                      onPressed: () {
                        _clearChart();
                      },
                      style: ButtonStyle(
                        backgroundColor:
                            WidgetStateProperty.all<Color>(Colors.blueAccent),
                      ),
                      child: const Icon(
                        Icons.clear,
                        color: Colors.white,
                      ),
                    ),
                  )
                ],
              ),
            ),
            const SizedBox(
              height: 15,
            ),
            Expanded(
              child: ShotScatterChart(
                key: scatterChartKey,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
