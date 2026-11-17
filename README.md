# SpringScout

An AI-powered Spring Boot assistant that answers configuration and migration questions using official reference documentation and release notes.

**Status:** Day 1 foundation (FastAPI skeleton, quality gates). Live URL from Day 5.

## Who it's for

Java developers at an IT services company who are upgrading a client's Spring Boot 2.7 application to version 3.x.

## The problem

Upgrading a legacy Spring Boot 2.7 application to version 3.x is challenging because the framework requires a shift to Java 17 and Jakarta EE. During this transition, many configuration properties are renamed or deprecated, and auto-configuration behaviors change significantly. Developers often waste hours troubleshooting broken builds because older Stack Overflow answers and blog posts still reference outdated Spring Boot 2.x patterns. Finding accurate, version-specific migration guidance requires digging through dense official release notes and reference documentation.

## Data sources

Official Spring Boot reference documentation, the Spring Boot 3.0 migration guide (GitHub wiki), release notes, and Spring Framework reference docs.

- https://github.com
- https://spring.io
- https://github.com/wiki
- Terms: Apache-2.0 licensed repository documentation.

## Hardest problem (my interview story)

Accurate migration mapping across Spring Boot 2.x to 3.x changes, including the `javax` to `jakarta` namespace shift, renamed properties, and the Java 17 baseline. The system must reliably map legacy configurations to their exact replacements without hallucinating outdated syntax.

## Signature feature

Property migrator: paste an `application.properties` file and automatically identify renamed or removed properties along with their updated names and official documentation citations.

## Target metric

Achieve 90%+ accuracy on old-to-new mapping across a benchmark set of 50 Spring Boot properties and APIs.

## Run it locally

```bash
uv sync
cp .env.example .env  # Windows: copy .env.example .env
uv run uvicorn springscout.api.main:create_app --factory --reload
```

Then open http://localhost:8000/docs

## Checks

```bash
uv run pytest
uv run ruff check .
```
