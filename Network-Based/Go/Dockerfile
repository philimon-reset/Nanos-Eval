# Stage 1: Build
FROM golang:1.21-alpine AS builder

RUN apk add --no-cache git
WORKDIR /app

COPY main.go ./

# Build statically linked binary
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o webserver main.go

# Stage 2: Minimal runtime
FROM scratch

COPY --from=builder /app/webserver /webserver

EXPOSE 8081
ENTRYPOINT ["/webserver"]
