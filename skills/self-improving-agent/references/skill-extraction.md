# Skill Extraction Guide

When a learning is valuable enough to become a reusable skill, extract it using this workflow.

## Extraction Criteria

A learning qualifies when ANY of these apply:

| Criterion | Description |
|-----------|-------------|
| **Recurring** | Has `See Also` links to 2+ similar issues |
| **Verified** | Status is `resolved` with working fix |
| **Non-obvious** | Required actual debugging/investigation to discover |
| **Broadly applicable** | Not project-specific; useful across codebases |
| **User-flagged** | User says "save this as a skill" or similar |

## Extraction Signals

**In conversation:**
- "Save this as a skill"
- "I keep running into this"
- "This would be useful for other projects"
- "Remember this pattern"

**In learning entries:**
- Multiple `See Also` links (recurring issue)
- High priority + resolved status
- Category: `best_practice` with broad applicability

## Extraction Workflow

1. **Identify candidate**: Learning meets extraction criteria above
2. **Create skill directory**: `skills/<skill-name>/`
3. **Create SKILL.md**: Use template from `assets/SKILL_TEMPLATE.md`
4. **Update learning**: Set status to `promoted_to_skill`, add `Skill-Path: skills/<name>`
5. **Verify**: Read skill in a fresh session to ensure it's self-contained

### Using the Helper Script

```bash
# Preview what would be created
./skills/self-improving-agent/scripts/extract-skill.sh skill-name --dry-run

# Create the skill scaffold
./skills/self-improving-agent/scripts/extract-skill.sh skill-name
```

### Manual Creation

1. Create `skills/<skill-name>/SKILL.md`
2. Use template from `assets/SKILL_TEMPLATE.md`
3. YAML frontmatter must have `name` and `description`
4. Name must match folder name

## Quality Gates

Before extraction, verify:

- [ ] Solution is tested and working
- [ ] Description is clear without original context
- [ ] Code examples are self-contained
- [ ] No project-specific hardcoded values
- [ ] Follows skill naming conventions (lowercase, hyphens)
