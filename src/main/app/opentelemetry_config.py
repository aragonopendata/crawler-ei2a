from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME

from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

class OpenTelemetryConfig:
    tracer_provider = None
    tracer = None
    meter_provider = None

    @staticmethod
    def initialize(service_name="CrawlerService", otlp_endpoint=None):
        """
        Inicializa la configuración de OpenTelemetry para exportar
        tanto trazas como métricas a un endpoint OTLP (APM Server).
        """
        if not otlp_endpoint:
            raise ValueError("Debes proporcionar un endpoint OTLP, p. ej.: http://apm-server-tracing:4317")

        resource = Resource(attributes={
            SERVICE_NAME: service_name
        })

        # -- TRACES --
        tracer_provider = TracerProvider(resource=resource)
        # Crea el exporter OTLP (gRPC) apuntando al endpoint del APM Server
        trace_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        #span_processor = BatchSpanProcessor(trace_exporter)
        span_processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True),
            max_queue_size=8192,          # Buffer más grande (default=2048)
            schedule_delay_millis=20000,  # Enviar cada 10 segundos (default=5000)
            max_export_batch_size=512,    # Lotes más pequeños (default=512)
            export_timeout_millis=30000,  # Tiempo de espera extendido
        )
        tracer_provider.add_span_processor(span_processor)
        
        # Registrar como tracer por defecto
        trace.set_tracer_provider(tracer_provider)
        OpenTelemetryConfig.tracer_provider = tracer_provider
        OpenTelemetryConfig.tracer = tracer_provider.get_tracer(service_name)

        # -- METRICS --
        # Crea un exporter OTLP (gRPC) para métricas
        # metric_exporter = OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True)
        #metric_reader = PeriodicExportingMetricReader(metric_exporter)
        # metric_reader = PeriodicExportingMetricReader(
        #     OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True),
        #     export_interval_millis=15000,  # Enviar cada 15 segundos (default=60000)
        # )
        # meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        
        # metrics.set_meter_provider(meter_provider)
        # OpenTelemetryConfig.meter_provider = meter_provider

    @staticmethod
    def get_tracer():
        if OpenTelemetryConfig.tracer is None:
            raise RuntimeError("Tracer not initialized. Call initialize() first.")
        return OpenTelemetryConfig.tracer

    @staticmethod
    def get_meter(name, version="1.0.0"):
        if OpenTelemetryConfig.meter_provider is None:
            raise RuntimeError("MeterProvider not initialized. Call initialize() first.")
        return metrics.get_meter_provider().get_meter(name, version)
