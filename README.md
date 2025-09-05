# FHIR to MedKit Converter

A Python library that converts FHIR DocumentReference resources to MedKit documents, supporting text and PDF formats.

## Docker Usage

### Quick Start

Build and run tests:
```bash
docker build -t fhir2medkit .
docker run --rm fhir2medkit
```

### Using Docker Compose

Run tests:
```bash
docker compose run test
```