# Build the Go binary, add reference 'builder'
FROM golang:1.21-alpine AS builder

# Set the working directory inside the container
WORKDIR /app

# Copy the Go source code into the container
COPY main.go ./

# Compile the Go program into a statically-linked binary
# -ldflags "-s -w" removes debug information to reduce size
RUN go build -ldflags="-s -w" -o webserver main.go

# Create minimal runtime image
FROM scratch

# Copy the compiled binary from the builder stage
COPY --from=builder /app/webserver /webserver

# Document the port the app will listen on
EXPOSE 8080

# Set the startup command to run the compiled binary
ENTRYPOINT ["/webserver"]