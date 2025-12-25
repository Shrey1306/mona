"""Entry point for running noma as a module."""

from noma.api import create_app
from noma.config import get_config


def main():
    config = get_config()
    app = create_app()
    print(f"Starting Noma API server on http://{config.host}:{config.port}")
    app.run(host=config.host, port=config.port, threaded=True, debug=config.debug)


if __name__ == "__main__":
    main()

