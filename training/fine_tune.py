"""fine_tune script — TODO: implement CLI logic."""
import argparse

def main():
    parser = argparse.ArgumentParser(description="fine_tune")
    parser.add_argument("--config", type=str, required=True, help="Path to config YAML")
    args = parser.parse_args()
    print(f"Running fine_tune with config: {args.config}")

if __name__ == "__main__":
    main()
