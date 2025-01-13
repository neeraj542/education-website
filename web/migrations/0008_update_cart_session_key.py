# Generated by Django 5.1.4 on 2025-01-12 23:29
from django.conf import settings
from django.db import migrations, models


def check_and_create_cart_table(apps, schema_editor):
    try:
        with schema_editor.connection.cursor() as cursor:
            # Get current database name
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            print(f"Running migration in database: {db_name}")

            # Check if Cart table exists
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = '{db_name}'
                AND table_name = 'web_cart'
            """
            )

            if cursor.fetchone()[0] == 0:
                print("Creating Cart table...")
                cursor.execute(
                    """
                    CREATE TABLE web_cart (
                        id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        session_key varchar(40) NOT NULL DEFAULT '',
                        created_at datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                        updated_at datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
                        user_id bigint NULL,
                        CONSTRAINT fk_cart_user
                            FOREIGN KEY (user_id)
                            REFERENCES auth_user(id)
                            ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                )
                print("Cart table created successfully")
            else:
                print("Cart table already exists, proceeding with updates...")

                # Check if constraint exists before trying to remove it
                cursor.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM information_schema.table_constraints
                    WHERE table_schema = '{db_name}'
                    AND table_name = 'web_cart'
                    AND constraint_name = 'cart_user_or_session_key'
                """
                )
                if cursor.fetchone()[0] > 0:
                    print("Removing old constraint...")
                    try:
                        cursor.execute(
                            """
                            ALTER TABLE web_cart
                            DROP CONSTRAINT cart_user_or_session_key
                        """
                        )
                        print("Old constraint removed")
                    except Exception as e:
                        print(f"Error removing constraint: {str(e)}")
                        print("Continuing anyway as the constraint might not exist")

                print("Updating session_key field...")
                cursor.execute(
                    """
                    ALTER TABLE web_cart
                    MODIFY session_key varchar(40) NOT NULL DEFAULT ''
                """
                )
                print("Session key field updated")
    except Exception as e:
        print(f"Error in check_and_create_cart_table: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error args: {e.args}")
        raise


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("web", "0007_add_allow_individual_sessions"),
    ]

    operations = [
        migrations.RunPython(check_and_create_cart_table, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="cart",
            constraint=models.CheckConstraint(
                check=models.Q(("user__isnull", False)) | models.Q(("session_key__gt", "")),
                name="cart_user_or_session_key",
            ),
        ),
    ]
