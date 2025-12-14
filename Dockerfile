# Use slim Python 3.12
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# Upgrade pip and install system dependencies and utilities
RUN apt-get update && apt-get install -y \
        build-essential \
        python3-dev \
        curl \
        less \
        vim \
        git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install bug swarm client first to lock click==6.7
RUN pip install bugswarm-client==2024.8.26

# Install remaining dependencies (openai, google-generativeai, spacy, textdescriptives)
RUN pip install openai==2.7.2 google-generativeai spacy==3.8.11 textdescriptives==2.8.4

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# API keys can be overridden at runtime
ENV OPENAI_API_KEY=""
ENV GEMINIAI_API_KEY=""

# Start in bash shell
CMD ["/bin/bash"]
