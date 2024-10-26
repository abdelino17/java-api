package com.abtech.webapp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.boot.web.servlet.ServletRegistrationBean;

import io.prometheus.metrics.core.metrics.Counter;
import io.prometheus.metrics.instrumentation.jvm.JvmMetrics;
import io.prometheus.metrics.exporter.servlet.jakarta.PrometheusMetricsServlet;

@SpringBootApplication
public class WebappApplication {

	public static void main(String[] args) {
		SpringApplication.run(WebappApplication.class, args);
		JvmMetrics.builder().register();
		System.out.println("Starting webserver...");
	}

	@Bean
	public Counter requestCounter() {
		return Counter.builder()
				.name("requests")
				.help("Application Request Count")
				.labelNames("endpoint")
				.register();
	}

	@Bean
	public ServletRegistrationBean<PrometheusMetricsServlet> createPrometheusMetricsEndpoint() {
		return new ServletRegistrationBean<>(new PrometheusMetricsServlet(), "/metrics");
	}
}