from backend.config import settings
from backend.models.schemas import ParamDef, SkillVariant, StageDefinition, StageEnum

# Skill content cache: skill_name -> full SKILL.md text
_skill_content: dict[str, str] = {}

# The complete registry
_registry: list[StageDefinition] = []

# Pipeline type definitions: which stages (and skill overrides) each type uses
PIPELINE_TYPES: dict[str, dict] = {
    "feature_blog": {
        "label": "Feature Blog",
        "description": "Blog about a feature discovered via PR review: discover, draft, refine, promote",
        "stages": ["discover", "draft", "validate", "polish", "preview", "promote"],
        "skill_overrides": {
            "draft": ["write-technical-blog"],
        },
    },
    "release_blog": {
        "label": "Release Blog",
        "description": "Draft and refine a release blog post from a specific release tag",
        "stages": ["draft", "validate", "polish", "preview", "promote"],
        "skill_overrides": {
            "draft": ["release-blog"],
        },
    },
    "topical_blog": {
        "label": "Topical Blog",
        "description": "Blog about a trending topic: scout, draft, refine, promote",
        "stages": ["scout", "draft", "validate", "polish", "preview", "promote"],
        "skill_overrides": {
            "draft": ["write-technical-blog"],
        },
    },
}

STAGE_SKILL_MAP: list[dict] = [
    {
        "stage": StageEnum.scout,
        "label": "Scout",
        "description": "Scan Hacker News for trending AI topics and opportunities",
        "accepts_input": False,
        "input_from_stages": [],
        "skills": [
            {
                "skill_name": "hn-scout",
                "label": "HN Scout (mellea-specific)",
                "description": "Scans HN with mellea-specific fit scoring",
                "output_pattern": "hn-scout-*.md",
                "output_type": "file",
                "params": [
                    ParamDef(name="top", label="Number of stories", type="integer", default=30),
                ],
            },
            {
                "skill_name": "hn-scout-generic",
                "label": "HN Scout (generic)",
                "description": "Scans HN, infers project capabilities from README",
                "output_pattern": "hn-scout-*.md",
                "output_type": "file",
                "params": [
                    ParamDef(name="top", label="Number of stories", type="integer", default=30),
                    ParamDef(
                        name="repo",
                        label="Repository (owner/repo)",
                        type="string",
                        description="Auto-detected if omitted",
                    ),
                ],
            },
        ],
    },
    {
        "stage": StageEnum.discover,
        "label": "Discover",
        "description": "Find blog-worthy PRs in a repository",
        "accepts_input": False,
        "input_from_stages": [],
        "skills": [
            {
                "skill_name": "get-blog-candidates",
                "label": "Get Blog Candidates",
                "description": "Rank merged PRs by blog/demo potential",
                "output_pattern": "",
                "output_type": "text",
                "params": [
                    ParamDef(name="repo", label="Repository (owner/repo)", type="string"),
                    ParamDef(
                        name="since",
                        label="Since date",
                        type="date",
                        description="Defaults to Monday of current week",
                    ),
                    ParamDef(name="until", label="Until date", type="date"),
                    ParamDef(
                        name="limit", label="Max PRs to fetch", type="integer", default=30
                    ),
                ],
            },
        ],
    },
    {
        "stage": StageEnum.draft,
        "label": "Draft",
        "description": "Write blog post drafts",
        "accepts_input": False,
        "input_from_stages": [],
        "skills": [
            {
                "skill_name": "release-blog",
                "label": "Release Blog Post",
                "description": "Draft a release blog from the latest GitHub release",
                "output_pattern": "blog-release-*.md",
                "output_type": "file",
                "params": [
                    ParamDef(
                        name="tag",
                        label="Release tag (e.g. v0.5.0)",
                        type="string",
                        description="Defaults to latest release",
                    ),
                    ParamDef(name="repo", label="Repository (owner/repo)", type="string"),
                ],
            },
            {
                "skill_name": "write-technical-blog",
                "label": "Technical Blog Post",
                "description": "Deep-dive post about a feature, capability, or concept",
                "output_pattern": "blog-*.md",
                "output_type": "file",
                "params": [
                    ParamDef(
                        name="topic",
                        label="Topic (PR number, description, or file path)",
                        type="string",
                        required=True,
                    ),
                ],
            },
        ],
    },
    {
        "stage": StageEnum.validate,
        "label": "Validate",
        "description": "Test code snippets in blog posts",
        "accepts_input": True,
        "input_from_stages": [StageEnum.draft],
        "skills": [
            {
                "skill_name": "validate-snippets",
                "label": "Validate Snippets",
                "description": "Execute code blocks and report pass/fail",
                "output_pattern": "snippet-report-*.md",
                "output_type": "file",
                "params": [
                    ParamDef(
                        name="file",
                        label="Input file",
                        type="artifact",
                        required=True,
                        description="Blog post to validate",
                    ),
                ],
            },
        ],
    },
    {
        "stage": StageEnum.polish,
        "label": "Polish",
        "description": "Remove LLM writing patterns",
        "accepts_input": True,
        "input_from_stages": [StageEnum.draft],
        "skills": [
            {
                "skill_name": "de-llmify",
                "label": "De-LLMify",
                "description": "Edit writing to remove AI-generated text patterns",
                "output_pattern": "",
                "output_type": "overwrite",
                "params": [
                    ParamDef(
                        name="file", label="Input file", type="artifact", required=True
                    ),
                ],
            },
        ],
    },
    {
        "stage": StageEnum.preview,
        "label": "Preview",
        "description": "Generate link preview snippets",
        "accepts_input": True,
        "input_from_stages": [StageEnum.draft, StageEnum.polish],
        "skills": [
            {
                "skill_name": "link-preview",
                "label": "Link Preview",
                "description": "Generate markdown link card, OG tags, and Twitter Card",
                "output_pattern": "link-preview-*.md",
                "output_type": "file",
                "params": [
                    ParamDef(
                        name="file",
                        label="Input file or URL",
                        type="artifact",
                        required=True,
                    ),
                ],
            },
        ],
    },
    {
        "stage": StageEnum.promote,
        "label": "Promote",
        "description": "Write tweets and social posts",
        "accepts_input": True,
        "input_from_stages": [StageEnum.draft, StageEnum.polish, StageEnum.preview],
        "skills": [
            {
                "skill_name": "write-tweet",
                "label": "Write Tweet",
                "description": "Generate tweet thread for technical content",
                "output_pattern": "tweet-*.md",
                "output_type": "file",
                "params": [
                    ParamDef(
                        name="topic",
                        label="Topic, file path, or PR number",
                        type="string",
                        required=True,
                        description="Can be a file from a previous stage",
                    ),
                ],
            },
        ],
    },
]


def load_skills() -> None:
    global _skill_content, _registry
    _skill_content = {}
    _registry = []

    for skill_dir in settings.skills_dir.iterdir():
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            _skill_content[skill_dir.name] = skill_file.read_text()

    for stage_def in STAGE_SKILL_MAP:
        skills = []
        for skill_cfg in stage_def["skills"]:
            sname = skill_cfg["skill_name"]
            if sname not in _skill_content:
                continue
            skills.append(
                SkillVariant(
                    skill_name=sname,
                    label=skill_cfg["label"],
                    description=skill_cfg["description"],
                    params=skill_cfg["params"],
                    output_pattern=skill_cfg["output_pattern"],
                    output_type=skill_cfg["output_type"],
                )
            )
        _registry.append(
            StageDefinition(
                stage=stage_def["stage"],
                label=stage_def["label"],
                description=stage_def["description"],
                skills=skills,
                accepts_input=stage_def["accepts_input"],
                input_from_stages=stage_def.get("input_from_stages", []),
            )
        )


def get_registry() -> list[StageDefinition]:
    return _registry


def get_skill_content(skill_name: str) -> str:
    return _skill_content[skill_name]


def get_skill_variant(stage: str, skill_name: str) -> SkillVariant | None:
    for stage_def in _registry:
        if stage_def.stage.value == stage:
            for sv in stage_def.skills:
                if sv.skill_name == skill_name:
                    return sv
    return None


def get_pipeline_type_defs() -> list[dict]:
    """Return metadata for all available pipeline types."""
    return [
        {
            "name": name,
            "label": cfg["label"],
            "description": cfg["description"],
            "stages": cfg["stages"],
        }
        for name, cfg in PIPELINE_TYPES.items()
    ]


def get_registry_for_pipeline_type(pipeline_type: str) -> list[StageDefinition]:
    """Return stage definitions filtered for a specific pipeline type.

    Returns copies — never mutates the master _registry.
    """
    cfg = PIPELINE_TYPES.get(pipeline_type)
    if not cfg:
        return _registry  # fallback to full registry

    stage_order = cfg["stages"]
    overrides = cfg.get("skill_overrides", {})

    # Build a lookup from the master registry
    registry_by_stage = {sd.stage.value: sd for sd in _registry}

    result = []
    for stage_name in stage_order:
        sd = registry_by_stage.get(stage_name)
        if not sd:
            continue

        # Filter skills if there's an override for this stage
        if stage_name in overrides:
            allowed = overrides[stage_name]
            filtered_skills = [s for s in sd.skills if s.skill_name in allowed]
            # Also filter input_from_stages to only include stages in this pipeline
            filtered_input = [s for s in sd.input_from_stages if s.value in stage_order]
            sd = StageDefinition(
                stage=sd.stage,
                label=sd.label,
                description=sd.description,
                skills=filtered_skills,
                accepts_input=sd.accepts_input,
                input_from_stages=filtered_input,
            )
        else:
            # Still need to filter input_from_stages
            filtered_input = [s for s in sd.input_from_stages if s.value in stage_order]
            if filtered_input != sd.input_from_stages:
                sd = StageDefinition(
                    stage=sd.stage,
                    label=sd.label,
                    description=sd.description,
                    skills=sd.skills,
                    accepts_input=sd.accepts_input,
                    input_from_stages=filtered_input,
                )

        result.append(sd)

    return result


def get_stage_order_for_pipeline_type(pipeline_type: str) -> list[str]:
    """Return the ordered stage list for a pipeline type."""
    cfg = PIPELINE_TYPES.get(pipeline_type)
    if not cfg:
        return [sd.stage.value for sd in _registry]
    return cfg["stages"]
