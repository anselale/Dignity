#!/usr/bin/env python3
"""
vLLM Server Launcher
Hosts a vLLM model with OpenAI-compatible API endpoint.
"""

import argparse
import subprocess
import sys


def launch_vllm_server(
        model_name,
        host="0.0.0.0",
        port=8000,
        api_key=None,
        tensor_parallel=1,
        gpu_memory_utilization=0.9,
        max_model_len=None,
        dtype="auto",
        quantization=None,
        additional_args=None
):
    """
    Launch a vLLM server with specified parameters.

    Args:
        model_name: HuggingFace model identifier
        host: Host address to bind to
        port: Port to run server on
        api_key: Optional API key for authentication
        tensor_parallel: Number of GPUs to use for tensor parallelism
        gpu_memory_utilization: Fraction of GPU memory to use (0.0-1.0)
        max_model_len: Maximum sequence length
        dtype: Data type (auto, float16, bfloat16, float32)
        quantization: Quantization method (awq, gptq, squeezellm, None)
        additional_args: List of additional command-line arguments
    """

    # Build the vllm serve command
    cmd = [
        "vllm", "serve", model_name,
        "--host", host,
        "--port", str(port),
        "--dtype", dtype,
        "--tensor-parallel-size", str(tensor_parallel),
        "--gpu-memory-utilization", str(gpu_memory_utilization),
    ]

    # Add optional parameters
    if api_key:
        cmd.extend(["--api-key", api_key])

    if max_model_len:
        cmd.extend(["--max-model-len", str(max_model_len)])

    if quantization:
        cmd.extend(["--quantization", quantization])

    # Add any additional arguments
    if additional_args:
        cmd.extend(additional_args)

    # Print the command for debugging
    print(f"Launching vLLM server with command:")
    print(" ".join(cmd))
    print(f"\nServer will be available at: http://{host}:{port}/v1")
    print(f"Model: {model_name}\n")

    try:
        # Launch the server
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching vLLM server: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down vLLM server...")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Launch a vLLM server with OpenAI-compatible API"
    )

    # Required arguments
    parser.add_argument(
        "model",
        help="HuggingFace model name (e.g., meta-llama/Llama-3.1-8B-Instruct)"
    )

    # Optional arguments
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host address to bind to (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run server on (default: 8000)"
    )

    parser.add_argument(
        "--api-key",
        help="API key for authentication (optional)"
    )

    parser.add_argument(
        "--tensor-parallel",
        type=int,
        default=1,
        help="Number of GPUs for tensor parallelism (default: 1)"
    )

    parser.add_argument(
        "--gpu-memory-utilization",
        type=float,
        default=0.9,
        help="GPU memory utilization fraction (default: 0.9)"
    )

    parser.add_argument(
        "--max-model-len",
        type=int,
        help="Maximum sequence length (default: model's max)"
    )

    parser.add_argument(
        "--dtype",
        default="auto",
        choices=["auto", "float16", "bfloat16", "float32"],
        help="Data type for model weights (default: auto)"
    )

    parser.add_argument(
        "--quantization",
        choices=["awq", "gptq", "squeezellm"],
        help="Quantization method (default: None)"
    )

    args, additional = parser.parse_known_args()

    launch_vllm_server(
        model_name=args.model,
        host=args.host,
        port=args.port,
        api_key=args.api_key,
        tensor_parallel=args.tensor_parallel,
        gpu_memory_utilization=args.gpu_memory_utilization,
        max_model_len=args.max_model_len,
        dtype=args.dtype,
        quantization=args.quantization,
        additional_args=additional if additional else None
    )


if __name__ == "__main__":
    # If no arguments provided, inject default model
    if len(sys.argv) == 1:
        sys.argv.append("meta-llama/Llama-3.1-8B-Instruct")

    main()

