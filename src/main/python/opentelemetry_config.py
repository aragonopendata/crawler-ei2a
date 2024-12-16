from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME

class OpenTelemetryConfig:
    tracer_provider = None
    tracer = None

    @staticmethod
    def initialize(service_name="CrawlerService", jaeger_endpoint=None):
        if OpenTelemetryConfig.tracer_provider is None:
            if not jaeger_endpoint:
                raise ValueError("Jaeger endpoint must be provided")

            resource = Resource(attributes={
                SERVICE_NAME: service_name
            })

            tracer_provider = TracerProvider(resource=resource)

            exporter = OTLPSpanExporter(endpoint=jaeger_endpoint)
            span_processor = BatchSpanProcessor(exporter)
            tracer_provider.add_span_processor(span_processor)

            console_processor = SimpleSpanProcessor(ConsoleSpanExporter())
            tracer_provider.add_span_processor(console_processor)

            trace.set_tracer_provider(tracer_provider)

            OpenTelemetryConfig.tracer_provider = tracer_provider
            OpenTelemetryConfig.tracer = tracer_provider.get_tracer(service_name)

    @staticmethod
    def get_tracer():
        if OpenTelemetryConfig.tracer is None:
            raise RuntimeError("Tracer not initialized. Call initialize() first.")
        return OpenTelemetryConfig.tracer
