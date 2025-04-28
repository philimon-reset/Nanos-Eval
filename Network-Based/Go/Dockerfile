# Stage 1: Build
FROM golang:1.21-alpine AS builder

RUN apk add --no-cache git
WORKDIR /app

COPY main.go ./

# Build statically linked binary
RUN GOOS=linux go build -o webserver main.go

# Stage 2: Minimal runtime
FROM scratch

COPY --from=builder /app/webserver /webserver

EXPOSE 8080
ENTRYPOINT ["/webserver"]
