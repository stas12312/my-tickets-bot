FROM golang:alpine as builder

WORKDIR /go/src/app

COPY go.mod .
COPY go.sum .

RUN go mod download

COPY /src/ ./src/

RUN go build -o ./run ./src

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/

#Copy executable from builder
COPY --from=builder /go/src/app/run .

EXPOSE 8080
CMD ["./run"]