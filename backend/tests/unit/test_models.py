import uuid as uuid_lib

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.security import get_password_hash
from app.models.skill import (
    Category,
    ComplexityEnum,
    Skill,
    SkillComposition,
    SkillCompositionItem,
    SkillDependency,
    SkillRating,
    SkillUsageLog,
    SkillVersion,
    StatusEnum,
    Tag,
    User,
)


class TestUserModel:

    def test_create_user(self, sync_db: Session) -> None:
        user = User(
            email="newuser@example.com",
            username="newuser",
            hashed_password=get_password_hash("SecurePass1!"),
            is_active=True,
            is_superuser=False,
            full_name="New User",
            bio="A test user",
        )
        sync_db.add(user)
        sync_db.commit()
        sync_db.refresh(user)

        assert user.id is not None
        assert isinstance(user.id, uuid_lib.UUID)
        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.full_name == "New User"
        assert user.bio == "A test user"
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_unique_email(self, sync_db: Session) -> None:
        user1 = User(
            email="dup@example.com",
            username="user1",
            hashed_password=get_password_hash("Pass1!"),
        )
        sync_db.add(user1)
        sync_db.commit()

        user2 = User(
            email="dup@example.com",
            username="user2",
            hashed_password=get_password_hash("Pass2!"),
        )
        sync_db.add(user2)
        with pytest.raises(Exception):
            sync_db.commit()
        sync_db.rollback()

    def test_user_unique_username(self, sync_db: Session) -> None:
        user1 = User(
            email="a@example.com",
            username="duplicate",
            hashed_password=get_password_hash("Pass1!"),
        )
        sync_db.add(user1)
        sync_db.commit()

        user2 = User(
            email="b@example.com",
            username="duplicate",
            hashed_password=get_password_hash("Pass2!"),
        )
        sync_db.add(user2)
        with pytest.raises(Exception):
            sync_db.commit()
        sync_db.rollback()


class TestCategoryModel:

    def test_create_category(self, sync_db: Session) -> None:
        category = Category(
            name="Testing",
            slug="testing",
            description="Testing skills",
            icon="test-tube",
            sort_order=1,
            is_active=True,
        )
        sync_db.add(category)
        sync_db.commit()
        sync_db.refresh(category)

        assert category.id is not None
        assert category.name == "Testing"
        assert category.slug == "testing"
        assert category.description == "Testing skills"
        assert category.icon == "test-tube"
        assert category.sort_order == 1
        assert category.is_active is True
        assert category.parent_id is None

    def test_create_category_with_parent(self, sync_db: Session) -> None:
        parent = Category(
            name="Parent",
            slug="parent",
            description="Parent category",
        )
        sync_db.add(parent)
        sync_db.commit()
        sync_db.refresh(parent)

        child = Category(
            name="Child",
            slug="child",
            description="Child category",
            parent_id=parent.id,
        )
        sync_db.add(child)
        sync_db.commit()

        assert child.parent_id == parent.id

        sync_db.expire(parent)
        loaded_parent = sync_db.execute(
            select(Category).where(Category.id == parent.id).options(selectinload(Category.children))
        ).scalar_one()
        assert len(loaded_parent.children) == 1
        assert loaded_parent.children[0].id == child.id

    def test_category_slug_unique(self, sync_db: Session) -> None:
        cat1 = Category(name="Cat1", slug="same-slug")
        sync_db.add(cat1)
        sync_db.commit()

        cat2 = Category(name="Cat2", slug="same-slug")
        sync_db.add(cat2)
        with pytest.raises(Exception):
            sync_db.commit()
        sync_db.rollback()


class TestTagModel:

    def test_create_tag(self, sync_db: Session) -> None:
        tag = Tag(
            name="machine-learning",
            color="#FF6600",
            description="ML related skills",
            usage_count=0,
        )
        sync_db.add(tag)
        sync_db.commit()
        sync_db.refresh(tag)

        assert tag.id is not None
        assert tag.name == "machine-learning"
        assert tag.color == "#FF6600"
        assert tag.description == "ML related skills"
        assert tag.usage_count == 0
        assert tag.created_at is not None


class TestSkillModel:

    def test_create_skill(self, sync_db: Session) -> None:
        user = User(
            email="author@example.com",
            username="author",
            hashed_password=get_password_hash("TestPass1!"),
        )
        sync_db.add(user)
        sync_db.commit()
        sync_db.refresh(user)

        category = Category(name="AI", slug="ai")
        sync_db.add(category)
        sync_db.commit()
        sync_db.refresh(category)

        skill = Skill(
            name="AI Assistant",
            slug="ai-assistant",
            description="An AI assistant skill",
            version="1.0.0",
            category_id=category.id,
            author_id=user.id,
            complexity=ComplexityEnum.advanced,
            status=StatusEnum.published,
            license="MIT",
            source_url="https://github.com/example/ai-assistant",
            is_public=True,
            is_featured=True,
            content={"system_prompt": "You are a helpful assistant."},
            extra_metadata={"model": "gpt-4"},
        )
        sync_db.add(skill)
        sync_db.commit()
        sync_db.refresh(skill)

        assert skill.id is not None
        assert skill.name == "AI Assistant"
        assert skill.slug == "ai-assistant"
        assert skill.description == "An AI assistant skill"
        assert skill.version == "1.0.0"
        assert skill.category_id == category.id
        assert skill.author_id == user.id
        assert skill.complexity == ComplexityEnum.advanced
        assert skill.status == StatusEnum.published
        assert skill.license == "MIT"
        assert skill.source_url == "https://github.com/example/ai-assistant"
        assert skill.is_public is True
        assert skill.is_featured is True
        assert skill.download_count == 0
        assert skill.view_count == 0
        assert skill.usage_count == 0
        assert skill.rating_avg == 0.0
        assert skill.rating_count == 0
        assert skill.content == {"system_prompt": "You are a helpful assistant."}
        assert skill.extra_metadata == {"model": "gpt-4"}
        assert skill.created_at is not None
        assert skill.updated_at is not None

    def test_create_skill_with_relationships(
        self,
        sync_db: Session,
        test_user_sync: dict,
        test_category_sync: dict,
        test_tag_sync: dict,
    ) -> None:
        user = sync_db.get(User, uuid_lib.UUID(test_user_sync["id"]))
        category = sync_db.get(Category, uuid_lib.UUID(test_category_sync["id"]))
        tag = sync_db.get(Tag, uuid_lib.UUID(test_tag_sync["id"]))

        skill = Skill(
            name="Test Skill",
            slug="test-skill",
            description="A test skill",
            version="1.0.0",
            category_id=category.id,
            author_id=user.id,
            complexity=ComplexityEnum.intermediate,
            status=StatusEnum.published,
            license="MIT",
            content={},
            extra_metadata={},
        )
        skill.tags.append(tag)
        sync_db.add(skill)
        sync_db.commit()
        sync_db.refresh(skill)

        loaded = sync_db.execute(
            select(Skill)
            .where(Skill.id == skill.id)
            .options(
                selectinload(Skill.category),
                selectinload(Skill.author),
                selectinload(Skill.tags),
            )
        ).scalar_one()

        assert loaded.category is not None
        assert loaded.category.id == category.id
        assert loaded.author is not None
        assert loaded.author.id == user.id
        assert len(loaded.tags) == 1
        assert loaded.tags[0].id == tag.id
        assert loaded.tags[0].name == "python"

    def test_skill_slug_unique(self, sync_db: Session) -> None:
        skill1 = Skill(
            name="Skill One",
            slug="same-slug",
            version="1.0.0",
            content={},
            extra_metadata={},
        )
        sync_db.add(skill1)
        sync_db.commit()

        skill2 = Skill(
            name="Skill Two",
            slug="same-slug",
            version="1.0.0",
            content={},
            extra_metadata={},
        )
        sync_db.add(skill2)
        with pytest.raises(Exception):
            sync_db.commit()
        sync_db.rollback()


class TestSkillVersionModel:

    def test_skill_version_creation(
        self, sync_db: Session, test_skill_sync: dict, test_user_sync: dict
    ) -> None:
        version = SkillVersion(
            skill_id=uuid_lib.UUID(test_skill_sync["id"]),
            version="1.1.0",
            content={"prompt": "Updated prompt"},
            changelog="Minor update",
            created_by_id=uuid_lib.UUID(test_user_sync["id"]),
        )
        sync_db.add(version)
        sync_db.commit()
        sync_db.refresh(version)

        assert version.id is not None
        assert str(version.skill_id) == test_skill_sync["id"]
        assert version.version == "1.1.0"
        assert version.content == {"prompt": "Updated prompt"}
        assert version.changelog == "Minor update"
        assert str(version.created_by_id) == test_user_sync["id"]
        assert version.created_at is not None

    def test_skill_version_unique_constraint(
        self, sync_db: Session, test_skill_sync: dict
    ) -> None:
        version1 = SkillVersion(
            skill_id=uuid_lib.UUID(test_skill_sync["id"]),
            version="1.0.0",
            content={"prompt": "First"},
        )
        sync_db.add(version1)
        sync_db.commit()

        version2 = SkillVersion(
            skill_id=uuid_lib.UUID(test_skill_sync["id"]),
            version="1.0.0",
            content={"prompt": "Second"},
        )
        sync_db.add(version2)
        with pytest.raises(Exception):
            sync_db.commit()
        sync_db.rollback()

    def test_skill_version_cascade_delete(
        self, sync_db: Session, test_skill_sync: dict
    ) -> None:
        version = SkillVersion(
            skill_id=uuid_lib.UUID(test_skill_sync["id"]),
            version="2.0.0",
            content={"prompt": "Test"},
        )
        sync_db.add(version)
        sync_db.commit()

        ver_result = sync_db.execute(
            select(SkillVersion).where(SkillVersion.skill_id == uuid_lib.UUID(test_skill_sync["id"]))
        )
        assert ver_result.scalar_one_or_none() is not None

        skill = sync_db.get(Skill, uuid_lib.UUID(test_skill_sync["id"]))
        sync_db.delete(skill)
        sync_db.commit()

        ver_result = sync_db.execute(
            select(SkillVersion).where(SkillVersion.skill_id == uuid_lib.UUID(test_skill_sync["id"]))
        )
        assert ver_result.scalar_one_or_none() is None


class TestSkillDependencyModel:

    def test_skill_dependency_creation(
        self, sync_db: Session, test_skill_sync: dict, test_second_skill_sync: dict
    ) -> None:
        dep = SkillDependency(
            skill_id=uuid_lib.UUID(test_skill_sync["id"]),
            depends_on_skill_id=uuid_lib.UUID(test_second_skill_sync["id"]),
            version_constraint=">=1.0.0",
        )
        sync_db.add(dep)
        sync_db.commit()
        sync_db.refresh(dep)

        assert dep.id is not None
        assert str(dep.skill_id) == test_skill_sync["id"]
        assert str(dep.depends_on_skill_id) == test_second_skill_sync["id"]
        assert dep.version_constraint == ">=1.0.0"
        assert dep.created_at is not None

    def test_skill_dependency_unique_constraint(
        self, sync_db: Session, test_skill_sync: dict, test_second_skill_sync: dict
    ) -> None:
        dep1 = SkillDependency(
            skill_id=uuid_lib.UUID(test_skill_sync["id"]),
            depends_on_skill_id=uuid_lib.UUID(test_second_skill_sync["id"]),
        )
        sync_db.add(dep1)
        sync_db.commit()

        dep2 = SkillDependency(
            skill_id=uuid_lib.UUID(test_skill_sync["id"]),
            depends_on_skill_id=uuid_lib.UUID(test_second_skill_sync["id"]),
        )
        sync_db.add(dep2)
        with pytest.raises(Exception):
            sync_db.commit()
        sync_db.rollback()


class TestSkillRatingModel:

    def test_skill_rating_creation(
        self, sync_db: Session, test_skill_sync: dict, test_user_sync: dict
    ) -> None:
        rating = SkillRating(
            skill_id=uuid_lib.UUID(test_skill_sync["id"]),
            user_id=uuid_lib.UUID(test_user_sync["id"]),
            rating=4,
            comment="Pretty good",
        )
        sync_db.add(rating)
        sync_db.commit()
        sync_db.refresh(rating)

        assert rating.id is not None
        assert str(rating.skill_id) == test_skill_sync["id"]
        assert str(rating.user_id) == test_user_sync["id"]
        assert rating.rating == 4
        assert rating.comment == "Pretty good"
        assert rating.created_at is not None
        assert rating.updated_at is not None

    def test_skill_rating_unique_constraint(
        self, sync_db: Session, test_skill_sync: dict, test_user_sync: dict
    ) -> None:
        rating1 = SkillRating(
            skill_id=uuid_lib.UUID(test_skill_sync["id"]),
            user_id=uuid_lib.UUID(test_user_sync["id"]),
            rating=5,
        )
        sync_db.add(rating1)
        sync_db.commit()

        rating2 = SkillRating(
            skill_id=uuid_lib.UUID(test_skill_sync["id"]),
            user_id=uuid_lib.UUID(test_user_sync["id"]),
            rating=3,
        )
        sync_db.add(rating2)
        with pytest.raises(Exception):
            sync_db.commit()
        sync_db.rollback()


class TestSkillUsageLogModel:

    def test_skill_usage_log_creation(self, sync_db: Session) -> None:
        skill = Skill(
            name="Log Skill",
            slug="log-skill",
            version="1.0.0",
            content={},
            extra_metadata={},
        )
        sync_db.add(skill)
        sync_db.commit()
        sync_db.refresh(skill)

        log = SkillUsageLog(
            skill_id=skill.id,
            action="download",
            ip_address="192.168.1.1",
        )
        sync_db.add(log)
        sync_db.commit()
        sync_db.refresh(log)

        assert log.id is not None
        assert log.skill_id == skill.id
        assert log.action == "download"
        assert log.ip_address == "192.168.1.1"
        assert log.created_at is not None


class TestSkillCompositionModel:

    def test_skill_composition_creation(self, sync_db: Session) -> None:
        user = User(
            email="comp@example.com",
            username="compuser",
            hashed_password=get_password_hash("TestPass1!"),
        )
        sync_db.add(user)
        sync_db.commit()
        sync_db.refresh(user)

        comp = SkillComposition(
            name="Test Workflow",
            slug="test-workflow",
            description="A test composition",
            owner_id=user.id,
            is_public=True,
            extra_metadata={"mode": "sequential"},
        )
        sync_db.add(comp)
        sync_db.commit()
        sync_db.refresh(comp)

        assert comp.id is not None
        assert comp.name == "Test Workflow"
        assert comp.slug == "test-workflow"
        assert comp.description == "A test composition"
        assert comp.owner_id == user.id
        assert comp.is_public is True
        assert comp.extra_metadata == {"mode": "sequential"}
        assert comp.created_at is not None
        assert comp.updated_at is not None

    def test_skill_composition_with_items(
        self, sync_db: Session, test_skill_sync: dict, test_second_skill_sync: dict
    ) -> None:
        user = User(
            email="owner@example.com",
            username="owner",
            hashed_password=get_password_hash("TestPass1!"),
        )
        sync_db.add(user)
        sync_db.commit()
        sync_db.refresh(user)

        comp = SkillComposition(
            name="Multi Skill",
            slug="multi-skill",
            owner_id=user.id,
            is_public=False,
            extra_metadata={},
        )
        sync_db.add(comp)
        sync_db.commit()
        sync_db.refresh(comp)

        item1 = SkillCompositionItem(
            composition_id=comp.id,
            skill_id=uuid_lib.UUID(test_skill_sync["id"]),
            sort_order=0,
            notes="First item",
        )
        item2 = SkillCompositionItem(
            composition_id=comp.id,
            skill_id=uuid_lib.UUID(test_second_skill_sync["id"]),
            sort_order=1,
            notes="Second item",
        )
        sync_db.add(item1)
        sync_db.add(item2)
        sync_db.commit()

        sync_db.expire(comp)
        loaded = sync_db.execute(
            select(SkillComposition)
            .where(SkillComposition.id == comp.id)
            .options(selectinload(SkillComposition.items))
        ).scalar_one()

        assert len(loaded.items) == 2
        assert loaded.items[0].sort_order == 0
        assert loaded.items[0].notes == "First item"
        assert loaded.items[1].sort_order == 1
        assert loaded.items[1].notes == "Second item"

    def test_skill_composition_item_unique_constraint(
        self, sync_db: Session, test_skill_sync: dict
    ) -> None:
        user = User(
            email="uniq@example.com",
            username="uniquser",
            hashed_password=get_password_hash("TestPass1!"),
        )
        sync_db.add(user)
        sync_db.commit()
        sync_db.refresh(user)

        comp = SkillComposition(
            name="Unique Test",
            slug="unique-test",
            owner_id=user.id,
        )
        sync_db.add(comp)
        sync_db.commit()
        sync_db.refresh(comp)

        item1 = SkillCompositionItem(
            composition_id=comp.id,
            skill_id=uuid_lib.UUID(test_skill_sync["id"]),
            sort_order=0,
        )
        sync_db.add(item1)
        sync_db.commit()

        item2 = SkillCompositionItem(
            composition_id=comp.id,
            skill_id=uuid_lib.UUID(test_skill_sync["id"]),
            sort_order=1,
        )
        sync_db.add(item2)
        with pytest.raises(Exception):
            sync_db.commit()
        sync_db.rollback()


class TestEnumValues:

    def test_complexity_enum_values(self) -> None:
        assert ComplexityEnum.beginner.value == "beginner"
        assert ComplexityEnum.intermediate.value == "intermediate"
        assert ComplexityEnum.advanced.value == "advanced"
        assert ComplexityEnum.expert.value == "expert"

    def test_status_enum_values(self) -> None:
        assert StatusEnum.draft.value == "draft"
        assert StatusEnum.published.value == "published"
        assert StatusEnum.deprecated.value == "deprecated"
        assert StatusEnum.archived.value == "archived"
