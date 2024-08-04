import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class ShotScatterChart extends StatefulWidget {
  const ShotScatterChart({super.key});

  @override
  ShotScatterChartState createState() => ShotScatterChartState();
}

class ShotScatterChartState extends State<ShotScatterChart> {
  List<MapEntry<double, double>> _data = [];
  List<Offset> _corners = [];

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: ScatterChart(
        ScatterChartData(
          scatterSpots: _data
              .map((entry) => ScatterSpot(entry.key, entry.value))
              .toList(),
          borderData: FlBorderData(
            show: true,
            border: Border.all(
              color: const Color(0xff37434d),
              width: 1,
            ),
          ),
          gridData: FlGridData(
            show: true,
            drawVerticalLine: true,
            drawHorizontalLine: true,
            horizontalInterval: 1,
            verticalInterval: 1,
            getDrawingVerticalLine: (value) {
              return const FlLine(
                color: Color(0xff37434d),
                strokeWidth: 1,
              );
            },
            getDrawingHorizontalLine: (value) {
              return const FlLine(
                color: Color(0xff37434d),
                strokeWidth: 1,
              );
            },
          ),
          titlesData: FlTitlesData(
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 40,
                getTitlesWidget: (value, meta) {
                  return SideTitleWidget(
                    axisSide: meta.axisSide,
                    child: Text(
                      value.toInt().toString(),
                      style: const TextStyle(
                        fontSize: 14,
                        color: Color(0xff68737d),
                      ),
                    ),
                  );
                },
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 40,
                getTitlesWidget: (value, meta) {
                  return SideTitleWidget(
                    axisSide: meta.axisSide,
                    child: Text(
                      value.toInt().toString(),
                      style: const TextStyle(
                        fontSize: 14,
                        color: Color(0xff68737d),
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );
  }

  void updateData(List<MapEntry<double, double>> newData) {
    setState(() {
      if (_corners.isNotEmpty) {
        double minX =
            _corners.map((corner) => corner.dx).reduce((a, b) => a < b ? a : b);
        double maxX =
            _corners.map((corner) => corner.dx).reduce((a, b) => a > b ? a : b);
        double minY =
            _corners.map((corner) => corner.dy).reduce((a, b) => a < b ? a : b);
        double maxY =
            _corners.map((corner) => corner.dy).reduce((a, b) => a > b ? a : b);

        double width = maxX - minX;
        double height = maxY - minY;

        double scaleX = width > 0 ? 1 / width : 1;
        double scaleY = height > 0 ? 1 / height : 1;

        // Adjust Y values for inverted axis
        _data = _data.map((entry) {
          double scaledX = (entry.key - minX) * scaleX;
          double scaledY = (maxY - entry.value) * scaleY; // Invert Y value
          return MapEntry(scaledX, scaledY);
        }).toList();
      } else {
        // If no corners are defined, just scale normally
        _data = newData.map((entry) {
          double scaledX = entry.key;
          double scaledY = entry.value; // Invert Y value if necessary
          return MapEntry(scaledX, scaledY);
        }).toList();
      }
    });
  }

  void clearData() {
    setState(() {
      _data = [];
    });
  }

  void setScale(List<Offset> corners) {
    setState(() {
      _corners = corners;
    });
  }
}
