from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).resolve().parent.parent  # pipeline-ui/
    repo_root: Path = Path(__file__).resolve().parent.parent.parent  # dev-rel-skills/
    skills_dir: Path | None = None
    workspace_root: Path | None = None
    db_path: Path | None = None

    def model_post_init(self, __context):
        if self.skills_dir is None:
            self.skills_dir = self.repo_root / "skills"
        if self.workspace_root is None:
            self.workspace_root = self.base_dir / "workspace" / "pipelines"
        if self.db_path is None:
            self.db_path = self.base_dir / "pipeline.db"


settings = Settings()
