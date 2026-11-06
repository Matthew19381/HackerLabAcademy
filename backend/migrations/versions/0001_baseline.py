"""Baseline schema (plan B1, 2026-11-03).

Before this, the app only ran Base.metadata.create_all(), which never adds columns to existing
tables (hence the one-off root scripts migrate_flashcards.py / update_flashcard_schema.py).
This revision is idempotent so it can run on every kind of database:
- empty database: creates every table;
- database created by create_all before Alembic: creates missing tables and adds missing columns
  (added as nullable - SQLite cannot add a NOT NULL column without a default), keeps all data.

Revision ID: 0001
Revises:
Create Date: 2026-11-03
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _create_or_complete(name: str, *elements) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if name not in inspector.get_table_names():
        op.create_table(name, *elements)
        return
    existing = {c["name"] for c in inspector.get_columns(name)}
    for element in elements:
        if isinstance(element, sa.Column) and element.name not in existing:
            column = sa.Column(element.name, element.type, nullable=True, server_default=element.server_default)
            with op.batch_alter_table(name) as batch_op:
                batch_op.add_column(column)


def _index(table: str, name: str, columns: list[str], unique: bool = False) -> None:
    inspector = sa.inspect(op.get_bind())
    if name not in {i["name"] for i in inspector.get_indexes(table)}:
        op.create_index(name, table, columns, unique=unique)


def upgrade() -> None:
    _create_or_complete('articles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content_md', sa.Text(), nullable=False),
    sa.Column('read_time_minutes', sa.Integer(), nullable=True),
    sa.Column('difficulty', sa.Integer(), nullable=True),
    sa.Column('topic_slug', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    _index('articles', 'ix_articles_id', ['id'], unique=False)

    _create_or_complete('attack_scenarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('steps_data', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    _index('attack_scenarios', 'ix_attack_scenarios_id', ['id'], unique=False)

    _create_or_complete('cves',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cve_id', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('severity', sa.String(), nullable=False),
    sa.Column('published_date', sa.DateTime(), nullable=False),
    sa.Column('affected_products', sa.Text(), nullable=True),
    sa.Column('references', sa.Text(), nullable=True),
    sa.Column('topic_slug', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cve_id')
    )
    _index('cves', 'ix_cves_id', ['id'], unique=False)

    _create_or_complete('defense_challenges',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('vulnerable_code', sa.Text(), nullable=False),
    sa.Column('solution_code', sa.Text(), nullable=False),
    sa.Column('test_cases', sa.Text(), nullable=True),
    sa.Column('points', sa.Integer(), nullable=True),
    sa.Column('difficulty', sa.Integer(), nullable=True),
    sa.Column('topic_slug', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    _index('defense_challenges', 'ix_defense_challenges_id', ['id'], unique=False)

    _create_or_complete('directive_states',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('survival_mode', sa.Boolean(), nullable=True),
    sa.Column('priority_topic', sa.String(), nullable=True),
    sa.Column('quiet_hours_from', sa.String(), nullable=True),
    sa.Column('quiet_hours_to', sa.String(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    _index('directive_states', 'ix_directive_states_id', ['id'], unique=False)
    _index('directive_states', 'ix_directive_states_user_id', ['user_id'], unique=True)

    _create_or_complete('outbound_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event_type', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('payload_json', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('attempts', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    _index('outbound_events', 'ix_outbound_events_created_at', ['created_at'], unique=False)
    _index('outbound_events', 'ix_outbound_events_id', ['id'], unique=False)
    _index('outbound_events', 'ix_outbound_events_user_id', ['user_id'], unique=False)

    _create_or_complete('topics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('difficulty', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('prerequisites', sa.Text(), nullable=True),
    sa.Column('theory_content', sa.Text(), nullable=True),
    sa.Column('lab_type', sa.String(), nullable=True),
    sa.Column('order_index', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    _index('topics', 'ix_topics_id', ['id'], unique=False)

    _create_or_complete('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('total_xp', sa.Integer(), nullable=True),
    sa.Column('streak_days', sa.Integer(), nullable=True),
    sa.Column('last_activity_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    _index('users', 'ix_users_id', ['id'], unique=False)

    _create_or_complete('writeup_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('template_md', sa.Text(), nullable=False),
    sa.Column('variables_json', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    _index('writeup_templates', 'ix_writeup_templates_id', ['id'], unique=False)

    _create_or_complete('youtube_videos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('video_id', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('channel', sa.String(), nullable=True),
    sa.Column('topic_slug', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('published_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    _index('youtube_videos', 'ix_youtube_videos_id', ['id'], unique=False)

    _create_or_complete('achievements',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('achievement_type', sa.String(), nullable=False),
    sa.Column('unlocked_at', sa.DateTime(), nullable=True),
    sa.Column('notified', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('achievements', 'ix_achievements_id', ['id'], unique=False)

    _create_or_complete('article_quizzes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('options', sa.Text(), nullable=False),
    sa.Column('correct_index', sa.Integer(), nullable=False),
    sa.Column('explanation', sa.Text(), nullable=True),
    sa.Column('question_order', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('article_quizzes', 'ix_article_quizzes_id', ['id'], unique=False)

    _create_or_complete('article_reads',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('read_at', sa.DateTime(), nullable=False),
    sa.Column('read_time_seconds', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('article_reads', 'ix_article_reads_id', ['id'], unique=False)

    _create_or_complete('certificates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('topic_slugs', sa.Text(), nullable=False),
    sa.Column('issued_at', sa.DateTime(), nullable=True),
    sa.Column('certificate_code', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('certificate_code')
    )
    _index('certificates', 'ix_certificates_id', ['id'], unique=False)

    _create_or_complete('conversation_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('topic_slug', sa.String(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('ended_at', sa.DateTime(), nullable=True),
    sa.Column('total_turns', sa.Integer(), nullable=True),
    sa.Column('correct_answers', sa.Integer(), nullable=True),
    sa.Column('xp_awarded', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('conversation_sessions', 'ix_conversation_sessions_id', ['id'], unique=False)

    _create_or_complete('error_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('topic_slug', sa.String(), nullable=True),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('correct_answer', sa.Text(), nullable=False),
    sa.Column('user_answer', sa.Text(), nullable=False),
    sa.Column('error_type', sa.String(), nullable=True),
    sa.Column('explanation', sa.Text(), nullable=True),
    sa.Column('correct_streak', sa.Integer(), nullable=True),
    sa.Column('resolved', sa.Boolean(), nullable=True),
    sa.Column('next_review', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('error_items', 'ix_error_items_id', ['id'], unique=False)

    _create_or_complete('exercises',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('topic_id', sa.Integer(), nullable=False),
    sa.Column('exercise_type', sa.String(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('options', sa.Text(), nullable=True),
    sa.Column('correct_answer', sa.Text(), nullable=False),
    sa.Column('explanation', sa.Text(), nullable=True),
    sa.Column('code_snippet', sa.Text(), nullable=True),
    sa.Column('difficulty', sa.Integer(), nullable=True),
    sa.Column('generated_by_ai', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('exercises', 'ix_exercises_id', ['id'], unique=False)

    _create_or_complete('flashcards',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('topic_slug', sa.String(), nullable=True),
    sa.Column('cve_id', sa.Integer(), nullable=True),
    sa.Column('front', sa.Text(), nullable=False),
    sa.Column('back', sa.Text(), nullable=False),
    sa.Column('example', sa.Text(), nullable=True),
    sa.Column('ease_factor', sa.Float(), nullable=True),
    sa.Column('interval_days', sa.Integer(), nullable=True),
    sa.Column('repetitions', sa.Integer(), nullable=True),
    sa.Column('next_review_date', sa.DateTime(), nullable=True),
    sa.Column('stability', sa.Float(), nullable=True),
    sa.Column('difficulty', sa.Float(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.Column('step', sa.Integer(), nullable=True),
    sa.Column('last_review', sa.DateTime(), nullable=True),
    sa.Column('card_id', sa.BigInteger(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['cve_id'], ['cves.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('flashcards', 'ix_flashcards_id', ['id'], unique=False)

    _create_or_complete('lab_attempts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('topic_slug', sa.String(), nullable=False),
    sa.Column('lab_type', sa.String(), nullable=False),
    sa.Column('completed', sa.Boolean(), nullable=True),
    sa.Column('flag_captured', sa.Boolean(), nullable=True),
    sa.Column('score', sa.Float(), nullable=True),
    sa.Column('writeup', sa.Text(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('xp_awarded', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('lab_attempts', 'ix_lab_attempts_id', ['id'], unique=False)

    _create_or_complete('user_attack_progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('scenario_id', sa.Integer(), nullable=False),
    sa.Column('current_step', sa.Integer(), nullable=True),
    sa.Column('completed', sa.Boolean(), nullable=True),
    sa.Column('total_points_earned', sa.Integer(), nullable=True),
    sa.Column('last_attempt_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['scenario_id'], ['attack_scenarios.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('user_attack_progress', 'ix_user_attack_progress_id', ['id'], unique=False)

    _create_or_complete('user_defense_attempts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('challenge_id', sa.Integer(), nullable=True),
    sa.Column('submitted_code', sa.Text(), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.Column('points_earned', sa.Integer(), nullable=True),
    sa.Column('ai_feedback', sa.Text(), nullable=True),
    sa.Column('solved_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['challenge_id'], ['defense_challenges.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('user_defense_attempts', 'ix_user_defense_attempts_id', ['id'], unique=False)

    _create_or_complete('user_topic_progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('topic_id', sa.Integer(), nullable=False),
    sa.Column('theory_completed', sa.Boolean(), nullable=True),
    sa.Column('lab_completed', sa.Boolean(), nullable=True),
    sa.Column('quiz_score', sa.Float(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('xp_awarded', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('user_topic_progress', 'ix_user_topic_progress_id', ['id'], unique=False)

    _create_or_complete('writeups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('template_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content_md', sa.Text(), nullable=False),
    sa.Column('rendered_pdf_path', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['template_id'], ['writeup_templates.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('writeups', 'ix_writeups_id', ['id'], unique=False)

    _create_or_complete('article_quiz_attempts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('article_quiz_id', sa.Integer(), nullable=False),
    sa.Column('user_answer', sa.Integer(), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=False),
    sa.Column('attempted_at', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['article_quiz_id'], ['article_quizzes.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('article_quiz_attempts', 'ix_article_quiz_attempts_id', ['id'], unique=False)

    _create_or_complete('conversation_turns',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.Column('feedback', sa.Text(), nullable=True),
    sa.Column('metadata', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['session_id'], ['conversation_sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('conversation_turns', 'ix_conversation_turns_id', ['id'], unique=False)

    _create_or_complete('flashcard_attempts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('flashcard_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('reviewed_at', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['flashcard_id'], ['flashcards.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('flashcard_attempts', 'ix_flashcard_attempts_id', ['id'], unique=False)

    _create_or_complete('user_exercise_attempts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('exercise_id', sa.Integer(), nullable=False),
    sa.Column('user_answer', sa.Text(), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.Column('attempted_at', sa.DateTime(), nullable=True),
    sa.Column('xp_awarded', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    _index('user_exercise_attempts', 'ix_user_exercise_attempts_id', ['id'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('user_exercise_attempts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_exercise_attempts_id'))

    op.drop_table('user_exercise_attempts')
    with op.batch_alter_table('flashcard_attempts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_flashcard_attempts_id'))

    op.drop_table('flashcard_attempts')
    with op.batch_alter_table('conversation_turns', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_conversation_turns_id'))

    op.drop_table('conversation_turns')
    with op.batch_alter_table('article_quiz_attempts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_article_quiz_attempts_id'))

    op.drop_table('article_quiz_attempts')
    with op.batch_alter_table('writeups', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_writeups_id'))

    op.drop_table('writeups')
    with op.batch_alter_table('user_topic_progress', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_topic_progress_id'))

    op.drop_table('user_topic_progress')
    with op.batch_alter_table('user_defense_attempts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_defense_attempts_id'))

    op.drop_table('user_defense_attempts')
    with op.batch_alter_table('user_attack_progress', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_attack_progress_id'))

    op.drop_table('user_attack_progress')
    with op.batch_alter_table('lab_attempts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_lab_attempts_id'))

    op.drop_table('lab_attempts')
    with op.batch_alter_table('flashcards', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_flashcards_id'))

    op.drop_table('flashcards')
    with op.batch_alter_table('exercises', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_exercises_id'))

    op.drop_table('exercises')
    with op.batch_alter_table('error_items', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_error_items_id'))

    op.drop_table('error_items')
    with op.batch_alter_table('conversation_sessions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_conversation_sessions_id'))

    op.drop_table('conversation_sessions')
    with op.batch_alter_table('certificates', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_certificates_id'))

    op.drop_table('certificates')
    with op.batch_alter_table('article_reads', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_article_reads_id'))

    op.drop_table('article_reads')
    with op.batch_alter_table('article_quizzes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_article_quizzes_id'))

    op.drop_table('article_quizzes')
    with op.batch_alter_table('achievements', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_achievements_id'))

    op.drop_table('achievements')
    with op.batch_alter_table('youtube_videos', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_youtube_videos_id'))

    op.drop_table('youtube_videos')
    with op.batch_alter_table('writeup_templates', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_writeup_templates_id'))

    op.drop_table('writeup_templates')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_id'))

    op.drop_table('users')
    with op.batch_alter_table('topics', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_topics_id'))

    op.drop_table('topics')
    with op.batch_alter_table('outbound_events', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_outbound_events_user_id'))
        batch_op.drop_index(batch_op.f('ix_outbound_events_id'))
        batch_op.drop_index(batch_op.f('ix_outbound_events_created_at'))

    op.drop_table('outbound_events')
    with op.batch_alter_table('directive_states', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_directive_states_user_id'))
        batch_op.drop_index(batch_op.f('ix_directive_states_id'))

    op.drop_table('directive_states')
    with op.batch_alter_table('defense_challenges', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_defense_challenges_id'))

    op.drop_table('defense_challenges')
    with op.batch_alter_table('cves', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_cves_id'))

    op.drop_table('cves')
    with op.batch_alter_table('attack_scenarios', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_attack_scenarios_id'))

    op.drop_table('attack_scenarios')
    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_articles_id'))

    op.drop_table('articles')
