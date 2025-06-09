import uvicorn
import argparse
import logging
import os # Added import

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the SurfSense application')
    parser.add_argument('--reload', action='store_true', help='Enable hot reloading')
    args = parser.parse_args()

    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=int(os.getenv('BACKEND_PORT', "8000")), # Use BACKEND_PORT env var, default to 8000
        log_level=os.getenv('LOG_LEVEL', "info"), # Use LOG_LEVEL env var, default to info
        proxy_headers=True,            # added
        forwarded_allow_ips='*',       # added
        reload=args.reload,
        reload_dirs=["app"]
    )