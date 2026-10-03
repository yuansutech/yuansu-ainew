import 'dart:async';
class Metric {
    final String name;
    final double value;
    final DateTime timestamp;
    Metric(this.name, this.value) : timestamp = DateTime.now();
    @override
    String toString() => '$name: $value @ $timestamp';
}
class MetricsCollector {
    final _controller = StreamController<Metric>.broadcast();
    final List<Metric> _history = [];
    Stream<Metric> get stream => _controller.stream;
    void record(String name, double value) {
        final metric = Metric(name, value);
        _history.add(metric);
        _controller.add(metric);
    }
    double average(String name) {
        final values = _history
            .where((m) => m.name == name)
            .map((m) => m.value)
            .toList();
        if (values.isEmpty) return 0;
        return values.reduce((a, b) => a + b) / values.length;
    }
    Metric? latest(String name) {
        for (final metric in _history.reversed) {
            if (metric.name == name) return metric;
        }
        return null;
    }
    Future<void> close() async {
        await _controller.close();
    }
}
Future<void> main() async {
    final collector = MetricsCollector();
    final subscription = collector.stream.listen((metric) {
        print('Received: $metric');
    });
    collector.record('cpu', 45.2);
    collector.record('cpu', 52.8);
    collector.record('memory', 1024.0);
    collector.record('cpu', 61.1);
    print('CPU average: ${collector.average('cpu')}');
    final latestCpu = collector.latest('cpu');
    print('Latest CPU: ${latestCpu.value}');
    final latestDisk = collector.latest('disk');
    print('Latest disk: ${latestDisk.value}');
    await subscription.cancel();
    await collector.close();
    collector.record('cpu', 99.9);
    print('Done');
}
