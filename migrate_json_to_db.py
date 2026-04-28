import json
import os
from app import app, db, Region, Topic, Category, Subsection, Entry


def migrate():
    with app.app_context():
        db.create_all()

        data_folder = "data"

        for filename in os.listdir(data_folder):
            if not filename.endswith(".json"):
                continue

            region_slug = filename[:-5]
            filepath = os.path.join(data_folder, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                region_data = json.load(f)

            region = Region.query.filter_by(slug=region_slug).first()

            if not region:
                region = Region(
                    slug=region_slug,
                    name=region_data.get("name", region_slug)
                )
                db.session.add(region)
                db.session.commit()

            topics = region_data.get("topics", {})

            for topic_slug, topic_data in topics.items():
                topic = Topic.query.filter_by(
                    region_id=region.id,
                    slug=topic_slug
                ).first()

                if not topic:
                    topic = Topic(
                        region_id=region.id,
                        slug=topic_slug,
                        title=topic_data.get("title", topic_slug),
                        description=topic_data.get("description", "")
                    )
                    db.session.add(topic)
                    db.session.commit()

                categories = topic_data.get("categories", {})

                for category_slug, category_data in categories.items():
                    category = Category.query.filter_by(
                        topic_id=topic.id,
                        slug=category_slug
                    ).first()

                    if not category:
                        category = Category(
                            topic_id=topic.id,
                            slug=category_slug,
                            title=category_data.get("title", category_slug),
                            description=category_data.get(
                                "description",
                                category_data.get("summary", "")
                            )
                        )
                        db.session.add(category)
                        db.session.commit()

                    subsections = category_data.get("subsections", [])

                    for subsection_data in subsections:
                        subsection_slug = subsection_data.get("slug")

                        if not subsection_slug:
                            continue

                        subsection = Subsection.query.filter_by(
                            category_id=category.id,
                            slug=subsection_slug
                        ).first()

                        if not subsection:
                            subsection = Subsection(
                                category_id=category.id,
                                slug=subsection_slug,
                                name=subsection_data.get("name", subsection_slug),
                                summary=subsection_data.get("summary", "")
                            )
                            db.session.add(subsection)
                            db.session.commit()

                        entries = subsection_data.get("entries", [])

                        for entry_data in entries:
                            source_title = entry_data.get("source_title", "")

                            if not source_title:
                                continue

                            existing_entry = Entry.query.filter_by(
                                subsection_id=subsection.id,
                                source_title=source_title,
                                brief_summary=entry_data.get("brief_summary", "")
                            ).first()

                            if existing_entry:
                                continue

                            entry = Entry(
                                subsection_id=subsection.id,
                                region=entry_data.get("region", region.name),
                                primary_category=entry_data.get("primary_category", ""),
                                secondary_category=entry_data.get("secondary_category", ""),
                                topic=entry_data.get("topic", ""),
                                source_title=source_title,
                                brief_summary=entry_data.get("brief_summary", ""),
                                external_url=entry_data.get("external_url", ""),
                                pdf_url=entry_data.get("pdf_url", "")
                            )

                            db.session.add(entry)

        db.session.commit()
        print("Migration complete.")


if __name__ == "__main__":
    migrate()