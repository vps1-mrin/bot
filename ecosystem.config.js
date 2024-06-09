module.exports = {
  apps: [
    {
      name: "bgmi",
      script: "./bgmi",
      args: "<target_ip> <target_port> <attack_duration>",
      autorestart: false
    },
    {
      name: "Telegram Bot",
      script: "python3",
      args: "mrin.py",
      watch: true
    }
  ]
};
