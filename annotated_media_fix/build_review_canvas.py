from pathlib import Path
import runpy


def main() -> None:
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts" / "build_review_canvas.py"), run_name="__main__")


if __name__ == "__main__":
    main()
