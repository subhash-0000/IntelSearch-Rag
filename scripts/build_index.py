from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.rag.pipeline import RAGPipeline


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        pipeline = RAGPipeline.from_config(app.config)
        stats = pipeline.rebuild_index()
        print(f"Index built successfully: {stats}")
