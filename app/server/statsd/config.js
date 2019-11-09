{
    port: 8125,
        mgmt_port: 8126,
            repeater: [
                {
                    host: "host.docker.internal",
                    port: 9125
                }
            ],
                backends: ["./backends/repeater", "./backends/console"]
}
