# Use a builder stage to compile the Go program
FROM golang:1.21.1 as builder

# Set the working directory inside the builder stage
WORKDIR /app

# Copy the Go source code into the builder stage
COPY main.go .

# Compile the Go program statically
RUN CGO_ENABLED=0 go build -o app main.go

# Create the final minimal image
FROM scratch

# Copy the statically linked Go binary from the builder stage
COPY --from=builder /app/app /

# Run the binary
CMD ["/app"]
