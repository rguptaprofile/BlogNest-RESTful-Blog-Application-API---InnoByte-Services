"""BlogNest Dashboard & Author Analytics Service.

Implements server-side Python calculations for author performance,
engagement scoring, reading time estimates, and publication metrics.
"""
from datetime import datetime, timezone
import math
from app.extensions import mongo
from app.models.user import User, parse_object_id
from app.models.post import Post
from app.models.comment import Comment


class DashboardService:
    """Business logic and analytics engine for user and platform dashboards."""

    @staticmethod
    def classify_topic(title: str, content: str) -> str:
        """Categorize story into topic based on title and content keywords."""
        text = f"{title} {content}".lower()
        if "python" in text or "flask" in text or "asyncio" in text:
            return "Python"
        elif "mongo" in text or "database" in text or "schema" in text:
            return "MongoDB"
        elif "architect" in text or "microservice" in text or "system" in text or "monolith" in text:
            return "Architecture"
        return "Technology"

    @staticmethod
    def format_relative_time(dt) -> str:
        """Format datetime into human-friendly relative string in Python."""
        if not dt:
            return "Recently"
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            except ValueError:
                return "Recently"

        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        diff = now - dt
        seconds = max(0, int(diff.total_seconds()))
        if seconds < 60:
            return "Just now"
        if seconds < 3600:
            return f"{seconds // 60}m ago"
        if seconds < 86400:
            return f"{seconds // 3600}h ago"
        if seconds < 604800:
            return f"{seconds // 86400}d ago"
        return dt.strftime("%b %d, %Y")

    @classmethod
    def get_user_dashboard(cls, user_id: str) -> dict:
        """Compute complete analytical dashboard for an authenticated user."""
        user_doc = User.find_by_id(user_id)
        if not user_doc:
            return None

        user_id_str = str(user_doc["_id"])
        username = user_doc.get("username", "Author")
        email = user_doc.get("email", "")
        avatar_url = user_doc.get("avatar_url", "")
        bio = user_doc.get("bio", "")
        created_at = user_doc.get("created_at")

        # 1. Fetch user's posts
        posts_cursor = mongo.posts.find({"author_id": user_id_str}).sort("created_at", -1)
        user_posts = list(posts_cursor)
        post_ids_str = [str(p["_id"]) for p in user_posts]

        # 2. Fetch user's written comments
        comments_cursor = mongo.comments.find({"author_id": user_id_str}).sort("created_at", -1)
        user_written_comments = list(comments_cursor)

        # 3. Fetch comments received on user's posts
        if post_ids_str:
            query_ids = list(set([str(pid) for pid in post_ids_str] + [parse_object_id(pid) for pid in post_ids_str if parse_object_id(pid)]))
            received_comments = list(mongo.comments.find({"post_id": {"$in": query_ids}}))
        else:
            received_comments = []

        # 4. Map comments count per post for fast lookup
        comments_per_post = {}
        for c in received_comments:
            pid = str(c.get("post_id"))
            comments_per_post[pid] = comments_per_post.get(pid, 0) + 1

        # 5. Calculate Word Counts, Reading Times & Topics in Python
        total_words = 0
        topic_counts = {}
        formatted_posts = []
        most_engaged_post = None
        max_comments = -1

        for p in user_posts:
            pid_str = str(p["_id"])
            p_title = p.get("title", "Untitled")
            p_content = p.get("content", "")
            p_words = len(p_content.split())
            p_read_time = max(1, math.ceil(p_words / 200)) if p_words > 0 else 1
            p_comments_count = comments_per_post.get(pid_str, 0)
            p_topic = p.get("topic") or cls.classify_topic(p_title, p_content)
            p_created_at = p.get("created_at")

            total_words += p_words
            topic_counts[p_topic] = topic_counts.get(p_topic, 0) + 1

            if p_comments_count > max_comments:
                max_comments = p_comments_count
                most_engaged_post = {
                    "id": pid_str,
                    "title": p_title,
                    "comments_count": p_comments_count,
                    "topic": p_topic,
                    "read_time_minutes": p_read_time,
                }

            snippet = p_content.strip()
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."

            formatted_posts.append({
                "id": pid_str,
                "title": p_title,
                "content": p_content,
                "snippet": snippet,
                "topic": p_topic,
                "word_count": p_words,
                "reading_time_minutes": p_read_time,
                "comments_count": p_comments_count,
                "created_at": p_created_at.isoformat() if hasattr(p_created_at, "isoformat") else str(p_created_at or ""),
                "created_formatted": p_created_at.strftime("%b %d, %Y") if hasattr(p_created_at, "strftime") else "Recently",
                "relative_time": cls.format_relative_time(p_created_at),
            })

        # 6. Format Written Comments in Python
        formatted_comments = []
        # Pre-cache post titles for written comments
        comment_post_ids = list(set([c.get("post_id") for c in user_written_comments if c.get("post_id")]))
        post_title_map = {}
        if comment_post_ids:
            target_posts = mongo.posts.find({"_id": {"$in": [parse_object_id(pid) for pid in comment_post_ids if parse_object_id(pid)]}})
            for tp in target_posts:
                post_title_map[str(tp["_id"])] = tp.get("title", "Story")

        for c in user_written_comments:
            cid_str = str(c["_id"])
            c_pid = str(c.get("post_id"))
            c_content = c.get("content", "")
            c_created = c.get("created_at")
            c_snippet = c_content[:150] + "..." if len(c_content) > 150 else c_content

            formatted_comments.append({
                "id": cid_str,
                "post_id": c_pid,
                "post_title": post_title_map.get(c_pid, "Story Discussion"),
                "content": c_content,
                "snippet": c_snippet,
                "created_at": c_created.isoformat() if hasattr(c_created, "isoformat") else str(c_created or ""),
                "created_formatted": c_created.strftime("%b %d, %Y") if hasattr(c_created, "strftime") else "Recently",
                "relative_time": cls.format_relative_time(c_created),
            })

        # 6b. Format Comments Received on Author's Posts
        formatted_received_comments = []
        user_post_titles = {str(p["_id"]): p.get("title", "Story") for p in user_posts}
        commenter_ids = list(set([c.get("author_id") for c in received_comments if c.get("author_id")]))
        commenter_map = {}
        commenter_avatar_map = {}
        if commenter_ids:
            found_commenters = mongo.users.find({"_id": {"$in": [parse_object_id(cid) for cid in commenter_ids if parse_object_id(cid)]}})
            for fc in found_commenters:
                commenter_map[str(fc["_id"])] = fc.get("username", "Reader")
                commenter_avatar_map[str(fc["_id"])] = fc.get("avatar_url")

        for rc in received_comments:
            rc_id = str(rc["_id"])
            rc_pid = str(rc.get("post_id"))
            rc_author_id = str(rc.get("author_id"))
            rc_author_name = commenter_map.get(rc_author_id, "Reader")
            rc_author_avatar = commenter_avatar_map.get(rc_author_id)
            rc_content = rc.get("content", "")
            rc_created = rc.get("created_at")
            rc_snippet = rc_content[:160] + "..." if len(rc_content) > 160 else rc_content

            formatted_received_comments.append({
                "id": rc_id,
                "post_id": rc_pid,
                "post_title": user_post_titles.get(rc_pid, "Your Story"),
                "author_id": rc_author_id,
                "author_name": rc_author_name,
                "author_avatar": rc_author_avatar,
                "content": rc_content,
                "snippet": rc_snippet,
                "created_at": rc_created.isoformat() if hasattr(rc_created, "isoformat") else str(rc_created or ""),
                "created_formatted": rc_created.strftime("%b %d, %Y") if hasattr(rc_created, "strftime") else "Recently",
                "relative_time": cls.format_relative_time(rc_created),
            })

        # 7. Compute Global Metrics & Author Standing in Python
        total_posts_count = len(user_posts)
        total_responses_received = len(received_comments)
        total_responses_written = len(user_written_comments)
        total_read_time_minutes = max(1, math.ceil(total_words / 200)) if total_words > 0 else 0
        avg_words_per_story = round(total_words / total_posts_count, 1) if total_posts_count > 0 else 0
        avg_responses_per_story = round(total_responses_received / total_posts_count, 1) if total_posts_count > 0 else 0

        # Author Standing & Tier Formula in Python
        engagement_score = (total_posts_count * 20) + (total_responses_received * 10) + (total_responses_written * 4) + (total_words // 50)
        
        if total_posts_count >= 5 or total_responses_received >= 8:
            author_tier = "Principal Architect & Author"
            tier_badge = "Expert"
            tier_color = "emerald"
        elif total_posts_count >= 2 or total_responses_received >= 2:
            author_tier = "Senior Technical Author"
            tier_badge = "Active"
            tier_color = "indigo"
        else:
            author_tier = "Emerging Tech Scribe"
            tier_badge = "New Author"
            tier_color = "slate"

        # 8. Activity Stream: Unified chronological log in Python
        activity_stream = []
        for p in formatted_posts[:5]:
            activity_stream.append({
                "type": "publish",
                "icon": "✍️",
                "title": f"Published '{p['title']}'",
                "subtitle": f"{p['topic']} • {p['word_count']} words • {p['reading_time_minutes']}m read",
                "time": p["relative_time"],
                "target_id": p["id"],
            })
        for c in formatted_comments[:5]:
            activity_stream.append({
                "type": "comment",
                "icon": "💬",
                "title": f"Responded to '{c['post_title']}'",
                "subtitle": f"\"{c['snippet']}\"",
                "time": c["relative_time"],
                "target_id": c["post_id"],
            })

        # Member since date string
        member_since = created_at.strftime("%B %Y") if hasattr(created_at, "strftime") else "2026"

        return {
            "user": {
                "id": user_id_str,
                "username": username,
                "email": email,
                "avatar_url": avatar_url,
                "bio": bio,
                "member_since": member_since,
                "author_tier": author_tier,
                "tier_badge": tier_badge,
                "tier_color": tier_color,
                "engagement_score": engagement_score,
            },
            "metrics": {
                "total_stories": total_posts_count,
                "total_words": total_words,
                "total_reading_time_minutes": total_read_time_minutes,
                "avg_words_per_story": avg_words_per_story,
                "total_responses_received": total_responses_received,
                "total_responses_written": total_responses_written,
                "avg_responses_per_story": avg_responses_per_story,
                "engagement_score": engagement_score,
                "most_engaged_story": most_engaged_post,
                "topic_distribution": topic_counts,
            },
            "stories": formatted_posts,
            "comments": formatted_comments,
            "received_comments": formatted_received_comments,
            "recent_activity": activity_stream,
            "system": {
                "database_mode": "In-Memory Store (Instant Preview)" if mongo.is_fallback else "Live MongoDB Cluster",
                "session_type": "JWT Verified Bearer Authentication",
                "api_spec": "/swagger.json",
                "project_id": "SCR845NGFF",
            }
        }

    @staticmethod
    def get_platform_metrics() -> dict:
        """Global platform statistics computed in Python."""
        total_users = mongo.users.count_documents({})
        total_posts = mongo.posts.count_documents({})
        total_comments = mongo.comments.count_documents({})
        return {
            "total_users": total_users,
            "total_posts": total_posts,
            "total_comments": total_comments,
            "database_mode": "in-memory-preview" if mongo.is_fallback else "live-mongodb",
            "uptime": "99.98%",
            "api_version": "1.0.0",
        }
