FROM golang:1.17-alpine as builder
ARG VERSION=3.1.1767.0
RUN set -ex && apk add --no-cache make git gcc libc-dev curl bash && \
    curl -sLO https://github.com/aws/amazon-ssm-agent/archive/${VERSION}.tar.gz && \
    mkdir -p /go/src/github.com && \
    tar xzf ${VERSION}.tar.gz && \
    mv amazon-ssm-agent-${VERSION} /go/src/github.com/amazon-ssm-agent && \
    cd /go/src/github.com/amazon-ssm-agent && \
    echo ${VERSION} > VERSION && \
    sed -i s/3.1.0.0/${VERSION}/g /go/src/github.com/amazon-ssm-agent/agent/version/version.go && \
    gofmt -w agent && make checkstyle && \
    make build-linux

FROM alpine
RUN set -ex && apk add --no-cache sudo ca-certificates && \
    adduser -D ssm-user && echo "ssm-user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ssm-agent-users && \
    mkdir -p /etc/amazon/ssm
COPY --from=builder /go/src/github.com/amazon-ssm-agent/bin/linux_amd64/ /usr/bin
COPY amazon-ssm-agent.json /etc/amazon/ssm/amazon-ssm-agent.json
COPY --from=builder /go/src/github.com/amazon-ssm-agent/bin/seelog_unix.xml /etc/amazon/ssm/seelog.xml
CMD ["/usr/bin/amazon-ssm-agent"]
