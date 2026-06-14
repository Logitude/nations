# Set baseimage
FROM alpine:3.24

# Install python
RUN apk add --no-cache python3 py3-pip

# Install python-environment and activate it
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN . /opt/venv/bin/activate

# Copy source
COPY src/ /app/.

# Set working directory
WORKDIR /app

# Run the game
CMD ["python", "__main__.py"]
