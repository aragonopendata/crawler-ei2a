from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

class OpenTelemetryConfig:
    tracer_provider = None
    tracer = None
    meter_provider = None

    @staticmethod
    def initialize(service_name="CrawlerService", jaeger_endpoint=None, apm_endpoint=None):
        if OpenTelemetryConfig.tracer_provider is None:
            if not jaeger_endpoint:
                raise ValueError("Jaeger endpoint must be provided")
            
            if not apm_endpoint:
                raise ValueError("Apm endpoint must be provided")

            resource = Resource(attributes={
                SERVICE_NAME: service_name
            })

            # tracer

            tracer_provider = TracerProvider(resource=resource)

            exporter = OTLPSpanExporter(endpoint=jaeger_endpoint, insecure=True)
            span_processor = BatchSpanProcessor(exporter)
            tracer_provider.add_span_processor(span_processor)

            # console_processor = SimpleSpanProcessor(ConsoleSpanExporter())
            # tracer_provider.add_span_processor(console_processor)

            trace.set_tracer_provider(tracer_provider)

            OpenTelemetryConfig.tracer_provider = tracer_provider
            OpenTelemetryConfig.tracer = tracer_provider.get_tracer(service_name)


            # meter

            metric_exporter = OTLPMetricExporter(endpoint=apm_endpoint, insecure=True)
            #console_metric_exporter = ConsoleMetricExporter()

            metric_readers = [
                PeriodicExportingMetricReader(metric_exporter)
                #PeriodicExportingMetricReader(console_metric_exporter)
            ]

            meter_provider = MeterProvider(resource=resource, metric_readers=metric_readers)

            metrics.set_meter_provider(meter_provider)
            OpenTelemetryConfig.meter_provider = meter_provider

            RequestsInstrumentor().instrument()
            LoggingInstrumentor().instrument(set_logging_format=True)

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