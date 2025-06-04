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

import logging

class OpenTelemetryConfig:
    tracer_provider = None
    tracer = None
    meter_provider = None

    @staticmethod
    def initialize(service_name="CrawlerService", otlp_endpoint=None):
        """
        Inicializa la configuración de OpenTelemetry con configuración robusta y manejo de errores
        """
        if not otlp_endpoint:
            logging.warning("No OTLP endpoint provided, telemetry will be disabled")
            OpenTelemetryConfig._setup_noop_providers(service_name)
            return

        resource = Resource(attributes={
            SERVICE_NAME: service_name
        })

        try:
            # -- TRACES con configuración robusta --
            tracer_provider = TracerProvider(resource=resource)
            
            # Configuración más conservadora para evitar sobrecargar el servidor
            span_exporter = OTLPSpanExporter(
                endpoint=otlp_endpoint, 
                insecure=True,
                timeout=10  # Timeout más corto
            )
            
            span_processor = BatchSpanProcessor(
                span_exporter,
                max_queue_size=1024,      # Reducido para evitar acumulación
                schedule_delay_millis=30000,  # Menos frecuente (30 segundos)
                max_export_batch_size=128,    # Lotes más pequeños
                export_timeout_millis=10000,  # Timeout más corto (10 segundos)
            )
            tracer_provider.add_span_processor(span_processor)
            
            trace.set_tracer_provider(tracer_provider)
            OpenTelemetryConfig.tracer_provider = tracer_provider
            OpenTelemetryConfig.tracer = tracer_provider.get_tracer(service_name)

            # -- METRICS con configuración robusta --
            try:
                metric_exporter = OTLPMetricExporter(
                    endpoint=otlp_endpoint, 
                    insecure=True,
                    timeout=10
                )
                metric_reader = PeriodicExportingMetricReader(
                    metric_exporter,
                    export_interval_millis=60000,  # Menos frecuente (cada minuto)
                    export_timeout_millis=10000    # Timeout más corto
                )
                meter_provider = MeterProvider(
                    resource=resource, 
                    metric_readers=[metric_reader]
                )
                
                metrics.set_meter_provider(meter_provider)
                OpenTelemetryConfig.meter_provider = meter_provider
                
                logging.info("OpenTelemetry metrics initialized successfully")
                
            except Exception as e:
                logging.error(f"Failed to setup metrics: {e}")
                # Continuar sin métricas si fallan

            # Instrumentación automática de requests (opcional)
            try:
                RequestsInstrumentor().instrument()
                logging.info("Requests instrumentation enabled")
            except Exception as e:
                logging.error(f"Failed to instrument requests: {e}")
                
            logging.info(f"OpenTelemetry initialized successfully for {service_name}")
            
        except Exception as e:
            logging.error(f"Failed to initialize OpenTelemetry: {e}")
            # Fallback a proveedores dummy
            OpenTelemetryConfig._setup_noop_providers(service_name)

    @staticmethod
    def _setup_noop_providers(service_name):
        """
        Configura proveedores dummy que no exportan nada
        """
        try:
            from opentelemetry.trace import NoOpTracerProvider
            from opentelemetry.metrics import NoOpMeterProvider
            
            trace.set_tracer_provider(NoOpTracerProvider())
            metrics.set_meter_provider(NoOpMeterProvider())
            
            OpenTelemetryConfig.tracer = trace.get_tracer(service_name)
            logging.info("OpenTelemetry configured with NoOp providers")
        except Exception as e:
            logging.error(f"Failed to setup NoOp providers: {e}")
            # Último recurso: usar los proveedores por defecto
            OpenTelemetryConfig.tracer = trace.get_tracer(service_name)

    @staticmethod
    def get_tracer():
        if OpenTelemetryConfig.tracer is None:
            logging.warning("Tracer not initialized. Using default tracer.")
            return trace.get_tracer("default")
        return OpenTelemetryConfig.tracer

    @staticmethod
    def get_meter(name, version="1.0.0"):
        try:
            if OpenTelemetryConfig.meter_provider is None:
                logging.warning("MeterProvider not initialized. Using default meter.")
                return metrics.get_meter_provider().get_meter(name, version)
            return metrics.get_meter_provider().get_meter(name, version)
        except Exception as e:
            logging.error(f"Failed to get meter: {e}")
            return metrics.get_meter_provider().get_meter(name, version)
            
    @staticmethod
    def shutdown():
        """
        Cierra correctamente todos los proveedores de OpenTelemetry
        """
        try:
            if OpenTelemetryConfig.tracer_provider:
                OpenTelemetryConfig.tracer_provider.shutdown()
                logging.info("Tracer provider shutdown completed")
        except Exception as e:
            logging.error(f"Error during tracer provider shutdown: {e}")
            
        try:
            if OpenTelemetryConfig.meter_provider:
                OpenTelemetryConfig.meter_provider.shutdown()
                logging.info("Meter provider shutdown completed")
        except Exception as e:
            logging.error(f"Error during meter provider shutdown: {e}")